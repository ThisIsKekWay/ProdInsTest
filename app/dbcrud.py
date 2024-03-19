from .database import async_session_maker
from .models import User, Advertisement, Comment, Category, Report
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

    @classmethod
    async def get_obj_with_pagination(cls, page: int, page_size: int, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).order_by(cls.model.id).filter_by(**filter_by)
            offset = (page - 1) * page_size
            items = await session.execute(query.offset(offset).limit(page_size))
            return items.scalars().all()


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



class CategoryCRUD(BaseCRUD):
    model = Category


class ReportCRUD(BaseCRUD):
    model = Report

    @classmethod
    async def get_report_with_pagination(cls, page: int, page_size: int):
        async with async_session_maker() as session:
            query = select(cls.model).order_by(cls.model.created_at.desc())
            offset = (page - 1) * page_size
            items = await session.execute(query.offset(offset).limit(page_size))
            return items.scalars().all()


class CommentCRUD(BaseCRUD):
    model = Comment

    @classmethod
    async def get_comments_with_pagination(cls, page: int, page_size: int, advertisement_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(advertisement_id=advertisement_id)
            offset = (page - 1) * page_size
            items = await session.execute(query.offset(offset).limit(page_size))
            return items.scalars().all()
