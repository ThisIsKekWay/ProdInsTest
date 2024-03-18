from fastapi import APIRouter, Depends, HTTPException

from app.dependences import get_current_user
from app.schemas import SAdvList, SAdvCreate
from app.dbcrud import AdvertisementCRUD

router = APIRouter(
    prefix="/adv",
    tags=["Advertising"],
    responses={404: {"description": "Not found"}},
)


@router.post("/all")
async def read_adv(avd_data: SAdvList):
    offset = avd_data.offset if hasattr(avd_data, "offset") else 0
    limit = avd_data.limit if hasattr(avd_data, "limit") else 10
    results = await AdvertisementCRUD.get_all_paginated(offset=offset, limit=limit)
    return results


@router.post("/create")
async def create_adv(adv_data: SAdvCreate, current_user=Depends(get_current_user)):
    if current_user:
        result = await AdvertisementCRUD.add(user_id=current_user.id, **adv_data.dict())
        return result
    raise HTTPException(status_code=401, detail="Not authorized")
