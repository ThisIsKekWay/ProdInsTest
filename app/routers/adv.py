from fastapi import APIRouter, Depends, HTTPException

from app.dependences import get_current_user
from app.schemas import SObjListFiltered, SAdvCreate, SReport, SGetItem, SAdvComment, SCommentsPag, SObjListUnfiltered
from app.dbcrud import AdvertisementCRUD, CategoryCRUD, ReportCRUD, CommentCRUD

router = APIRouter(
    prefix="/adv",
    tags=["Advertising"],
    responses={404: {"description": "Not found"}},
)


@router.post("/all")
async def get_all_advertisements(avd_data: SObjListUnfiltered):
    """
    Получить все объявления с пагинацией.

    Параметры:
    - avd_data: SObjListUnfiltered - Тело запроса, содержащее информацию о странице и размере страницы.

    Возвращает:
    - result: Результат получения объявлений с пагинацией.
    """
    result = await AdvertisementCRUD.get_obj_with_pagination(
        page=avd_data.page, page_size=avd_data.page_size,
    )
    return result


@router.post("/create")
async def create_adv(adv_data: SAdvCreate, current_user=Depends(get_current_user)):
    """
        Функция для создания объявления с заданными данными, если пользователь авторизован.

        Параметры:
        - adv_data: SAdvCreate - данные рекламы для создания
        - current_user: текущий авторизованный пользователь

        Возвращает:
        - dict: сообщение об успешном создании рекламы

        Вызывает:
        - HTTPException: если пользователь не авторизован или если указанная категория не найдена
    """
    if current_user:
        categories_list = await CategoryCRUD.get_find_all()
        categories_ids = [i.id for i in categories_list]
        if adv_data.category_id in categories_ids:
            await AdvertisementCRUD.add(user_id=current_user.id, **adv_data.dict())
            return {"message": "Advertisement has been created successfully"}
        raise HTTPException(status_code=404, detail="Category not found")
    raise HTTPException(status_code=401, detail="Not authorized")


@router.post('/adv_report')
async def adv_report(report_data: SReport, current_user=Depends(get_current_user)):
    """
        Функция для создания жалобы на объявление.
        Принимает report_data типа SReport и current_user в качестве параметров.
        Возвращает сообщение, указывающее на успешное создание жалобы.
    """
    if current_user:
        advertisement = await AdvertisementCRUD.find_one_or_none(id=report_data.adv_id)
        if advertisement:
            if current_user.id != advertisement.user_id:
                await ReportCRUD.add(creator_id=current_user.id,
                                     advertisement_id=advertisement.id,
                                     title=report_data.title,
                                     content=report_data.content,
                                     user_id=advertisement.user_id
                                     )
                return {"message": "Report has been created successfully"}
            raise HTTPException(status_code=403, detail="You can't report your own advertisement")
        raise HTTPException(status_code=404, detail="Advertisement not found")
    raise HTTPException(status_code=401, detail="Not authorized")


@router.post('/get_adv')
async def get_advertisement_by_id(target: SGetItem):
    """
        Функция, которая извлекает объявление по его идентификатору.

        Параметры:
        - target: SGetItem, целевой элемент для поиска.

        Возвращает:
        - объявление, если найдено, в противном случае вызывает HTTPException со статусным кодом 404.
    """
    advertisement = await AdvertisementCRUD.find_one_or_none(**target.dict())
    if advertisement:
        return advertisement
    raise HTTPException(status_code=404, detail="Advertisement not found")


@router.delete('/delete_adv')
async def delete_my_advertisement(target: SGetItem, current_user=Depends(get_current_user)):
    """
        Удалить объявление, указанное в target, если текущий пользователь имеет на это разрешение.

        Параметры:
        - target: SGetItem
        - current_user: Depends(get_current_user)

        Возвращает:
        - Dict: Сообщение, указывающее успешность или неуспешность удаления объявления
    """
    if current_user:
        advertisement = await AdvertisementCRUD.find_one_or_none(**target.dict())
        if advertisement:
            if current_user.id == advertisement.user_id:
                await AdvertisementCRUD.delete_by_id(**target.dict())
                return {"message": "Advertisement has been deleted successfully"}
            raise HTTPException(status_code=403, detail="You don't have enough permission")
        raise HTTPException(status_code=404, detail="Advertisement not found")
    raise HTTPException(status_code=401, detail="Not authorized")


@router.post('/set_commment')
async def set_comment(target_data: SAdvComment, current_user=Depends(get_current_user)):
    """
         Создать комментарий к объявлению, указанному в target_data, если текущий пользователь имеет на это разрешение.

         Параметры:
         - target_data: SAdvComment
         - current_user: Depends(get_current_user)

         Возвращает:
         - Dict: Сообщение, указывающее успешность или неуспешность создания комментария
     """
    if current_user:
        advertisement = await AdvertisementCRUD.find_one_or_none(id=target_data.advertisement_id)
        if advertisement:
            await CommentCRUD.add(user_id=current_user.id, **target_data.dict())
            return {"message": "Comment has been created successfully"}
        raise HTTPException(status_code=404, detail="Advertisement not found")
    raise HTTPException(status_code=401, detail="Not authorized")


@router.post('/get_comments')
async def get_comments_paginated_by_adv_id(target: SCommentsPag):
    """
        Получить комментарии с пагинацией для объявления, указанного в target.

        Параметры:
        - target: SCommentsPag

        Возвращает:
        - Dict: Комментарии с пагинацией для указанного объявления
    """
    advertisement = await AdvertisementCRUD.find_one_or_none(id=target.advertisement_id)
    if advertisement:
        return await CommentCRUD.get_comments_with_pagination(**target.dict())
    raise HTTPException(status_code=404, detail="Advertisement not found")


@router.post('/get_filtered_advs')
async def get_filtered_advertisements_by_cat_id(target: SObjListFiltered):
    """
        Получить отфильтрованные объявления по идентификатору категории.

        Параметры:
        - target: SObjListFiltered

        Возвращает:
        - List: Отфильтрованные объявления по указанному идентификатору категории
    """
    advertisements = await AdvertisementCRUD.get_obj_with_pagination(**target.dict())
    return advertisements
