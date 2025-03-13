from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum, func
from database import Base
from enums import UserRole, ReactionType


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    bio = Column(String)
    avatar = Column(String, nullable=True)
    user_type = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Reactions(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    reaction_type = Column(Enum(ReactionType), nullable=False)
    created_id = Column(DateTime, server_default=func.now())


class Comments(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"))
    content = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class Follows(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    following_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
