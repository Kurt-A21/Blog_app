from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    Enum as SQLAEnum,
    func,
    UUID,
)
from sqlalchemy.orm import relationship
from database import Base
import uuid
from constants import UserRole, ReactionType


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(UUID, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, index=True, unique=True, nullable=False)
    password = Column(String, nullable=False)
    bio = Column(Text, nullable=True)
    avatar = Column(String, nullable=True, default=None)  # add image path
    is_active = Column(Boolean, default=True)
    role = Column(SQLAEnum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, server_default=func.now(), nullable=True)

    posts = relationship("Posts", back_populates="user")
    comments = relationship("Comments", back_populates="user")
    reactions = relationship("Reactions", back_populates="user")


class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_by = Column(String)
    content = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    reactions = Column(SQLAEnum(ReactionType), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("Users", back_populates="posts")
    comments = relationship("Comments", back_populates="post")
    reactions = relationship("Reactions", back_populates="post")


class Comments(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    content = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("Users", back_populates="comments")
    post = relationship("Posts", back_populates="comments")
    reactions = relationship("Reactions", back_populates="comments")


class Reactions(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    reaction_type = Column(SQLAEnum(ReactionType), nullable=False)

    user = relationship("Users", back_populates="reactions")
    post = relationship("Posts", back_populates="reactions")
    comments = relationship("Comments", back_populates="reactions")


class Follows(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    following_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
