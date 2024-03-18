from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_banned = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_moderator = Column(Boolean, default=False)

    advertisements = relationship("Advertisement", back_populates="user", cascade="all, delete")
    comments = relationship("Comment", back_populates="user", cascade="all, delete")


class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    description = Column(Text)
    created_at = Column(Date, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="advertisements")
    comments = relationship("Comment", back_populates="advertisement", cascade="all, delete")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_at = Column(Date, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    advertisement_id = Column(Integer, ForeignKey("advertisements.id"))

    user = relationship("User", back_populates="comments")
    advertisement = relationship("Advertisement", back_populates="comments")
