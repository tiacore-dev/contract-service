from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, UploadFile, status
from loguru import logger
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import Contract, ContractFile
from app.pydantic_models.contract_file_models import (
    ContractFileCreateSchema,
    ContractFileEditSchema,
    ContractFileListResponseSchema,
    ContractFileResponseSchema,
    ContractFileSchema,
    contract_file_filter_params,
)
from app.s3.s3_manager import AsyncS3Manager

contract_file_router = APIRouter()


@contract_file_router.post(
    "/add",
    response_model=ContractFileResponseSchema,
    summary="Добавление файла к контракту",
    status_code=status.HTTP_201_CREATED,
)
async def add_contract_file(
    data: ContractFileCreateSchema = Body(...),
    context=Depends(require_permission_in_context("add_contract_file")),
):
    file_bytes = await data.file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Не удалось загрузить данные файла")
    logger.info(
        f"""Тип загружаемых данных: {type(file_bytes)}, 
            размер: {len(file_bytes)} байт"""
    )
    await validate_exists(Contract, data.contract_id, "Контракт")
    filename = data.file.filename or "Unknown"
    if "." in filename:
        name, extension = filename.rsplit(".", 1)
    else:
        name, extension = filename, ""

    manager = AsyncS3Manager()
    contract_id = data.contract_id
    s3_key = await manager.upload_bytes(file_bytes, str(contract_id), filename)
    contract_file = await ContractFile.create(
        contract_id=contract_id,
        s3_key=s3_key,
        name=name,
        extension=extension,
        created_by=context["user_id"],
        modified_by=context["user_id"],
    )
    if not contract_file:
        logger.error("Не удалось создать файла контракта")
        raise HTTPException(
            status_code=500, detail="Не удалось создать файла контракта"
        )

    logger.success(
        f"файла контракта {contract_file.name} ({contract_file.id}) успешно создан"
    )
    return ContractFileResponseSchema(contract_file_id=contract_file.id)


@contract_file_router.patch(
    "/{contract_file_id}",
    summary="Изменение файла контракта",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def edit_contract_file(
    contract_file_id: UUID = Path(
        ..., title="ID файла контракта", description="ID изменяемого файла контракта"
    ),
    data: ContractFileEditSchema = Body(...),
    context=Depends(require_permission_in_context("edit_contract_file")),
):
    logger.info(f"Обновление файла контракта {contract_file_id}")

    contract_file = (
        await ContractFile.filter(id=contract_file_id)
        .prefetch_related("contract")
        .first()
    )
    if not contract_file:
        logger.warning(f"файла контракта {contract_file_id} не найден")
        raise HTTPException(status_code=404, detail="файла контракта не найден")
    update_data = {}
    if data.file and not isinstance(data.file, UploadFile):
        raise HTTPException(status_code=400, detail="Недопустимый тип файла")
    if data.contract_id:
        contract_id = data.contract_id
        update_data["contract_id"] = contract_id
    else:
        contract_id = contract_file.contract.id
    if data.file:
        manager = AsyncS3Manager()
        file_bytes = await data.file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Не удалось загрузить файл")

        filename = data.file.filename or "Unknown"
        if "." in filename:
            name, extension = filename.rsplit(".", 1)
        else:
            name, extension = filename, ""
        contract_id_str = str(contract_id)

        await manager.delete_file(contract_file.s3_key)
        new_s3_key = await manager.upload_bytes(file_bytes, contract_id_str, filename)
        update_data["s3_key"] = new_s3_key
        update_data["name"] = name
        update_data["extension"] = extension
    contract_file.modified_by = context["user_id"]
    await contract_file.update_from_dict(update_data)
    await contract_file.save()
    return ContractFileResponseSchema(contract_file_id=contract_file.id)


@contract_file_router.delete(
    "/{contract_file_id}",
    summary="Удаление файла контракта",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_contract_file(
    contract_file_id: UUID = Path(
        ..., title="ID файла контракта", description="ID удаляемого файла контракта"
    ),
    _=Depends(require_permission_in_context("delete_contract_file")),
):
    contract_file = await ContractFile.filter(id=contract_file_id).first()
    if not contract_file:
        logger.warning(f"файла контракта {contract_file_id} не найден")
        raise HTTPException(status_code=404, detail="файла контракта не найден")
    manager = AsyncS3Manager()
    await manager.delete_file(contract_file.s3_key)
    await contract_file.delete()


@contract_file_router.get(
    "/all",
    response_model=ContractFileListResponseSchema,
    summary="Получение списка файла контрактаов с фильтрацией",
)
async def get_contract_files(
    filters: dict = Depends(contract_file_filter_params),
    _=Depends(require_permission_in_context("get_all_contract_files")),
):
    query = Q()

    if filters.get("contract_file_name"):
        query &= Q(name__icontains=filters["contract_file_name"])
    if filters.get("description"):
        query &= Q(description__icontains=filters["description"])

    order_by = f"{'-' if filters.get('order') == 'desc' else ''}{
        filters.get('sort_by', 'name')
    }"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)

    total_count = await ContractFile.filter(query).count()

    contract_files = (
        await ContractFile.filter(query)
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .values(
            "id",
            "name",
            "description",
            "created_at",
            "created_by",
            "modified_at",
            "modified_by",
        )
    )

    return ContractFileListResponseSchema(
        total=total_count,
        contract_files=[
            ContractFileSchema(**contract_file) for contract_file in contract_files
        ],
    )


@contract_file_router.get(
    "/{contract_file_id}/download", summary="Скачивание файла контракта"
)
async def download_contract_file(
    contract_file_id: UUID,
    _=Depends(require_permission_in_context("download_contract_file")),
):
    contract_file = await ContractFile.filter(id=contract_file_id).first()
    if not contract_file:
        raise HTTPException(status_code=404, detail="Файл контракта не найден")
    manager = AsyncS3Manager()
    url = await manager.generate_presigned_url(contract_file.s3_key)
    return {"url": url}


@contract_file_router.get(
    "/{contract_file_id}",
    response_model=ContractFileSchema,
    summary="Просмотр файла контракта",
)
async def get_contract_file(
    contract_file_id: UUID = Path(
        ...,
        title="ID файла контракта",
        description="ID просматриваемой файла контракта",
    ),
    _=Depends(require_permission_in_context("view_contract_file")),
):
    logger.info(f"Запрос на просмотр файла контракта: {contract_file_id}")
    contract_file = (
        await ContractFile.filter(id=contract_file_id)
        .first()
        .values(
            "id",
            "name",
            "description",
            "created_at",
            "created_by",
            "modified_at",
            "modified_by",
        )
    )

    if contract_file is None:
        logger.warning(f"файла контракта {contract_file_id} не найдена")
        raise HTTPException(status_code=404, detail="файла контракта не найдена")

    contract_file_schema = ContractFileSchema(**contract_file)

    logger.success(f"файла контракта найдена: {contract_file_schema}")
    return contract_file_schema
