from .database import async_session_maker
from .models import User, Advertisement, Comment
from sqlalchemy import select, insert, update, text
from sqlalchemy.orm import selectinload, load_only


class BaseCRUD:
    model = None

    @classmethod
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def delete_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            obj = await session.get(cls.model, model_id)
            if obj:
                await session.delete(obj)
                await session.commit()
                return {"message": "Object has been successefuly deleted"}
            return {"message": "Object not found"}

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def update_by_id(cls, model_id: int, **update_data):
        async with async_session_maker() as session:
            obj = await session.get(cls.model, model_id)
            if obj:
                for key, value in update_data.items():
                    setattr(obj, key, value)
                await session.commit()
                return {"message": "Object has been successefuly updated"}
            return {"message": "Object not found"}


class UserCRUD(BaseCRUD):
    model = User

    @classmethod
    async def find_by_username(cls, username: str):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(username=username)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_by_email(cls, email: str):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(email=email)
            result = await session.execute(query)
            return result.scalars().one_or_none()


class AdvertisementCRUD(BaseCRUD):
    model = Advertisement

    @classmethod
    async def find_by_title(cls, title: str):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(title=title)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def find_by_user_id(cls, user_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(user_id=user_id)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_all_paginated(cls, offset: int, limit: int):
        async with async_session_maker() as session:
            query = select(cls.model).offset(offset).limit(limit)
            result = await session.execute(query)
            return result.scalars().all()