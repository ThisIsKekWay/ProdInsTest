from fastapi import FastAPI
from app.routers import user, adv, admin

app = FastAPI()
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(adv.router)
