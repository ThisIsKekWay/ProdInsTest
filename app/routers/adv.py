from fastapi import APIRouter, Depends, HTTPException

from app.dependences import get_current_user
from app.schemas import SAdvList, SAdvCreate
from app.dbcrud import AdvertisementCRUD, CategoryCRUD

router = APIRouter(
    prefix="/adv",
    tags=["Advertising"],
    responses={404: {"description": "Not found"}},
)


@router.post("/all")
async def read_adv(avd_data: SAdvList):
    result = await AdvertisementCRUD.get_advs_with_pagination(
        page=avd_data.page, page_size=avd_data.page_size
    )
    return result


@router.post("/create")
async def create_adv(adv_data: SAdvCreate, current_user=Depends(get_current_user)):
    if current_user:
        categories_list = await CategoryCRUD.get_find_all()
        if adv_data.category_id not in categories_list:
            raise HTTPException(status_code=404, detail="Category not found")
        await AdvertisementCRUD.add(user_id=current_user.id, **adv_data.dict())
        return {"message": "Advertisement has been created successfully"}
    raise HTTPException(status_code=401, detail="Not authorized")
