from fastapi import APIRouter, HTTPException, Depends

from app.dbcrud import UserCRUD, AdvertisementCRUD, CommentCRUD, CategoryCRUD, ReportCRUD
from app.dependences import get_current_user
from app.schemas import SChangeState, SDelete, SCreateCategory, SMoveCategory, SObjList, SGetItem

router = APIRouter(
    prefix="/admin",
    tags=["For Admin zone"],
    responses={404: {"description": "Not found"}},
)


@router.post('/change_state')
async def change_user_state(user_data: SChangeState, current_user=Depends(get_current_user)):
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
async def get_all_reports_paginated(page_data: SObjList, current_user=Depends(get_current_user)):
    if current_user:
        if current_user.is_superuser or current_user.is_moderator:
            return await ReportCRUD.get_obj_with_pagination(**page_data.dict())
        raise HTTPException(status_code=403, detail="You don't have enough permission")
    raise HTTPException(status_code=401, detail="Not authorized")


@router.post('/get_report')
async def get_report_by_id(target: SGetItem, current_user=Depends(get_current_user)):
    if current_user:
        if current_user.is_superuser or current_user.is_moderator:
            return await ReportCRUD.find_one_or_none(**target.dict())
        raise HTTPException(status_code=403, detail="You don't have enough permission")
    raise HTTPException(status_code=401, detail="Not authorized")
