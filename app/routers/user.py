from fastapi import APIRouter, HTTPException, Response, Depends
from app.schemas import SUserRegister, SUserLogin
from app.dbcrud import UserCRUD
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
