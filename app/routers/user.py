from fastapi import APIRouter, HTTPException, Response, Depends

from app.config import settings
from app.schemas import SUserRegister, SUserLogin, SReport
from app.dbcrud import UserCRUD, ReportCRUD, AdvertisementCRUD
from app.auth import get_password_hash, verify_password, create_access_token
from app.dependences import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["Users and Authorization"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register")
async def register(user_data: SUserRegister):
    user = await UserCRUD.find_one_or_none(email=user_data.email)
    if user:
        raise HTTPException(status_code=500, detail="User with this email already exists")
    if user_data.email in settings.SU_EMAIL:
        hashed_pwd = get_password_hash(user_data.password)
        await UserCRUD.add(username=user_data.username,
                           email=user_data.email,
                           hashed_password=hashed_pwd,
                           is_superuser=True,
                           is_moderator=True)
        return {"message": "Account has been created successfully. Granted superuser permissions"}
    hashed_pwd = get_password_hash(user_data.password)
    await UserCRUD.add(username=user_data.username, email=user_data.email, hashed_password=hashed_pwd)
    return {"message": "User has been created successfully"}


@router.post("/login")
async def login(response: Response, user_data: SUserLogin):
    user = await UserCRUD.find_one_or_none(email=user_data.email)
    if user:
        if not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Wrong password")
        if user.is_banned:
            raise HTTPException(status_code=401, detail="User is banned")
        access_token = create_access_token(data={"sub": user.id})
        response.set_cookie("ref_access_token", access_token)
        return {"message": "User has been logged in successfully"}
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie("ref_access_token")
    return {"message": "User has been logged out successfully"}


@router.get("/me")
async def me(user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authorized")
    return user


@router.post('/adv_report')
async def adv_report(report_data: SReport, current_user=Depends(get_current_user)):
    if current_user:
        advertisement = await AdvertisementCRUD.find_one_or_none(id=report_data.adv_id)
        if advertisement:
            await ReportCRUD.add(creator_id=current_user.id,
                                 adv_id=advertisement.id,
                                 title=report_data.title,
                                 content=report_data.content,
                                 user_id=advertisement.user_id
                                 )
        raise HTTPException(status_code=404, detail="Advertisement not found")
    raise HTTPException(status_code=401, detail="Not authorized")
