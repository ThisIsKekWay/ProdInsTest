from fastapi import APIRouter, HTTPException, Depends

from app.dbcrud import UserCRUD, AdvertisementCRUD, CommentCRUD, CategoryCRUD, ReportCRUD, SUserEmailsCRUD
from app.dependences import get_current_user
from app.schemas import (SChangeState, SDelete, SCreateCategory, SMoveCategory, SObjListUnfiltered,
                         SGetItem, SEmailUsage, SUserEmails)

router = APIRouter(
    prefix="/admin",
    tags=["For Admin zone"],
    responses={404: {"description": "Not found"}},
)


@router.post('/change_state')
async def change_user_state(user_data: SChangeState, current_user=Depends(get_current_user)):
    """
        Изменить состояние пользователя на основе предоставленных данных.

        Параметры:
        - user_data: SChangeState
        - current_user: Depends(get_current_user)

        Возвращает:
        - Dict: Сообщение, указывающее успешность или неуспешность изменения состояния пользователя
    """
    if current_user:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="You don't have enough permission")
        user = await UserCRUD.find_one_or_none(email=user_data.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user_data.param == 'ban':
            await UserCRUD.update_by_id(user.id, is_banned=True)
        if user_data.param == 'unban':
            await UserCRUD.update_by_id(user.id, is_banned=False)
        if user_data.param == 'promote':
            await UserCRUD.update_by_id(user.id, is_moderator=True)
        if user_data.param == 'demote':
            await UserCRUD.update_by_id(user.id, is_moderator=False)
        return {"message": "User has been changed successfully"}
    raise HTTPException(status_code=401, detail="Not authorized")


@router.delete('/delete')
async def delete_object(content_target: SDelete, current_user=Depends(get_current_user)):
    """
        Удалить объект в зависимости от типа указанного в content_target.

        Параметры:
        - content_target: SDelete
        - current_user: Depends(get_current_user)

        Возвращает:
        - Dict: Сообщение об успешном или неуспешном удалении объекта
    """
    if current_user:
        if current_user.is_superuser:
            data_type = content_target.type
            if data_type == 'user':
                user = await UserCRUD.find_one_or_none(id=content_target.id)
                if user:
                    await UserCRUD.delete_by_id(user.id)
                    return {"message": "User has been deleted successfully"}
            if data_type == 'adv':
                data = await AdvertisementCRUD.find_one_or_none(id=content_target.id)
                if data:
                    await AdvertisementCRUD.delete_by_id(data.id)
                    return {"message": "Advertisement has been deleted successfully"}
            if data_type == 'comment':
                data = await CommentCRUD.find_one_or_none(id=content_target.id)
                if data:
                    await CommentCRUD.delete_by_id(data.id)
                    return {"message": "Comment has been deleted successfully"}
            if data_type == 'category':
                data = await CategoryCRUD.find_one_or_none(id=content_target.id)
                if data:
                    await CategoryCRUD.delete_by_id(data.id)
                    return {"message": "Category has been deleted successfully"}
            if data_type == 'report':
                data = await ReportCRUD.find_one_or_none(id=content_target.id)
                if data:
                    await ReportCRUD.delete_by_id(data.id)
                    return {"message": "Report has been deleted successfully"}
            raise HTTPException(status_code=404, detail="Object not found")
        raise HTTPException(status_code=403, detail="You don't have enough permission")
    raise HTTPException(status_code=401, detail="Not authorized")


@router.post('/create_cat')
async def create_category(cat_name: SCreateCategory, current_user=Depends(get_current_user)):
    """
        Создать категорию с указанным именем, если текущий пользователь имеет на это разрешение.

        Параметры:
        - cat_name: SCreateCategory
        - current_user: Depends(get_current_user)

        Возвращает:
        - Dict: Сообщение об успешном или неуспешном создании категории
    """
    if current_user:
        if current_user.is_superuser:
            category = await CategoryCRUD.find_one_or_none(name=cat_name.name)
            if category:
                raise HTTPException(status_code=409, detail="Category already exists")
            await CategoryCRUD.add(name=cat_name.name)
            return {"message": f"Category {cat_name.name} has been created successfully"}
        raise HTTPException(status_code=403, detail="You don't have enough permission")
    raise HTTPException(status_code=401, detail="Not authorized")


@router.post("/move_item_to_category")
async def switch_advertisement_category(move_data: SMoveCategory, current_user=Depends(get_current_user)):
    """
        Переместить объявление в указанную категорию, если текущий пользователь имеет на это разрешение.

        Параметры:
        - move_data: SMoveCategory
        - current_user: Depends(get_current_user)

        Возвращает:
        - Dict: Сообщение об успешном или неуспешном перемещении объявления в категорию
    """
    if current_user:
        if current_user.is_superuser or current_user.is_moderator:
            adv = await AdvertisementCRUD.find_one_or_none(id=move_data.adv_id)
            if not adv:
                raise HTTPException(status_code=404, detail="Advertisement not found")
            cat = await CategoryCRUD.find_one_or_none(id=move_data.target_cat)
            if not cat:
                raise HTTPException(status_code=404, detail="Category not found")
            await AdvertisementCRUD.update_by_id(adv.id, category_id=cat.id)
            return {"message": "Advertisement has been moved to the category successfully"}
        raise HTTPException(status_code=403, detail="You don't have enough permission")
    raise HTTPException(status_code=401, detail="Not authorized")


@router.post('/get_reports')
async def get_all_reports_paginated(page_data: SObjListUnfiltered, current_user=Depends(get_current_user)):
    """
        Получить все репорты с пагинацией, если текущий пользователь имеет на это разрешение.

        Параметры:
        - page_data: SObjListUnfiltered
        - current_user: Depends(get_current_user)

        Возвращает:
        - Dict: Все отчеты с пагинацией
    """
    if current_user:
        if current_user.is_superuser or current_user.is_moderator:
            return await ReportCRUD.get_obj_with_pagination(**page_data.dict())
        raise HTTPException(status_code=403, detail="You don't have enough permission")
    raise HTTPException(status_code=401, detail="Not authorized")


@router.post('/get_report')
async def get_report_by_id(target: SGetItem, current_user=Depends(get_current_user)):
    """
        Получить репорт по его ID, если текущий пользователь имеет на это разрешение.

        Параметры:
        - target: SGetItem
        - current_user: Depends(get_current_user)

        Возвращает:
        - Dict: Отчет по его ID
    """
    if current_user:
        if current_user.is_superuser or current_user.is_moderator:
            return await ReportCRUD.find_one_or_none(**target.dict())
        raise HTTPException(status_code=403, detail="You don't have enough permission")
    raise HTTPException(status_code=401, detail="Not authorized")


@router.post('/get_user_list')
async def get_user_list(target: SObjListUnfiltered, current_user=Depends(get_current_user)):
    """
        Функция, которая извлекает список пользователей на основе предоставленных параметров target с пагинацией.
        Требуется, чтобы текущий пользователь имел разрешения суперпользователя или модератора.
        Если у пользователя есть необходимые разрешения, возвращает список пользователей с пагинацией.
        Если у пользователя недостаточно разрешений, вызывает исключение HTTPException с кодом 403.
        Если пользователь не авторизован, вызывает исключение HTTPException с кодом 401.
    """
    if current_user:
        if current_user.is_superuser or current_user.is_moderator:
            return await UserCRUD.get_obj_with_pagination(**target.dict())
        raise HTTPException(status_code=403, detail="You don't have enough permission")
    raise HTTPException(status_code=401, detail="Not authorized")


@router.post('/get_user')
async def get_user_by_id(target: SGetItem, current_user=Depends(get_current_user)):
    """
        Функция для получения пользователя по ID с заданными параметрами target и current_user.
        Возвращает HTTPException с кодом состояния 403, если текущий пользователь не имеет прав суперпользователя
        или модератора,
        и HTTPException с кодом состояния 401, если пользователь не авторизован.
    """
    if current_user:
        if current_user.is_superuser or current_user.is_moderator:
            return await UserCRUD.find_one_or_none(**target.dict())
        raise HTTPException(status_code=403, detail="You don't have enough permission")
    raise HTTPException(status_code=401, detail="Not authorized")


@router.post('/set_superuser_list')
async def set_superuser_list(target: SEmailUsage, current_user=Depends(get_current_user)):
    """
    Функция для установки списка суперпользователей на основе предоставленного использования электронной почты.
    Принимает 'target' в качестве параметра типа SEmailUsage и 'current_user' в качестве необязательного параметра.
    Возвращает сообщение, указывающее количество успешно добавленных суперпользовательских электронных писем,
    и вызывает HTTP-исключения из-за недостаточных прав или незалогиненого доступа.
    """
    if current_user:
        if current_user.is_superuser:
            counter = 0
            for email in target.emails:
                super_user = await SUserEmailsCRUD.find_one_or_none(email=email)
                if not super_user:
                    user = await UserCRUD.find_one_or_none(email=email)
                    if not user:
                        await SUserEmailsCRUD.add(email=email)
                        counter += 1
                    continue
                continue
            return {"message": "Successfully added {} superuser emails".format(counter)}
        raise HTTPException(status_code=403, detail="You don't have enough permission")
    raise HTTPException(status_code=401, detail="Not authorized")


@router.delete('/delete_super_user_email')
async def delete_super_user_email(target: SUserEmails, current_user=Depends(get_current_user)):
    """
    Функция для удаления суперпользователя на основе предоставленного адреса электронной почты.
    Принимает 'target' в качестве параметра типа SEmailUsage и 'current_user' в качестве параметров.
    Возвращает сообщение, указывающее успешность удаленных суперпользовательских электронных писем,
    и вызывает HTTP-исключения из-за недостаточных прав или незалогиненного доступа.
    """
    if current_user:
        if current_user.is_superuser:
            super_user_email = await SUserEmailsCRUD.find_one_or_none(email=target.email)
            if super_user_email:
                await SUserEmailsCRUD.delete_by_id(super_user_email.id)
                return {"message": "Successfully deleted superuser email"}
            raise HTTPException(status_code=404, detail="Superuser email not found")
        raise HTTPException(status_code=403, detail="You don't have enough permission")
    raise HTTPException(status_code=401, detail="Not authorized")
