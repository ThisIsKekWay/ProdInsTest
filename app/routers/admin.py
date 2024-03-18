from fastapi import APIRouter, HTTPException, Depends

from app.auth import get_password_hash
from app.dbcrud import UserCRUD
from app.config import settings
from app.dependences import get_current_user
from app.schemas import SChangeState, SDelete

router = APIRouter(
    prefix="/admin",
    tags=["For Admin zone"],
    responses={404: {"description": "Not found"}},
)


@router.post("/registerSU")
async def register_super_user():
    super_user = await UserCRUD.find_one_or_none(is_superuser=True)
    if super_user:
        raise HTTPException(status_code=500, detail="Superuser is already exists. You aren't allowed to create more")
    hashed_pwd = get_password_hash(settings.SU_PASSWORD)
    await UserCRUD.add(username=settings.SU_USERNAME,
                       email=settings.SU_EMAIL,
                       hashed_password=hashed_pwd,
                       is_superuser=True,
                       is_moderator=True)
    return {"message": "Superuser has been created successfully"}


@router.post('/changestate')
async def promote(user_data: SChangeState, current_user=Depends(get_current_user)):
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
async def delete(: SDelete, current_user=Depends(get_current_user)):
    if current_user:
        if current_user.is_superuser:
            data_type = user_data.param
            user = await UserCRUD.find_one_or_none(email=user_data.email)
            if user:
                await UserCRUD.delete_by_id(user.id)
                return {"message": "User has been deleted successfully"}
            raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(status_code=403, detail="You don't have enough permission")
    raise HTTPException(status_code=401, detail="Not authorized")

