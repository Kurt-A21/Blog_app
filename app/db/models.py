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
    UniqueConstraint,
)
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from .base_class import Base
import uuid
import json
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
    is_active = Column(Boolean, default=False)
    role = Column(SQLAEnum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    last_seen = Column(DateTime, nullable=True)

    posts = relationship("Posts", back_populates="user")
    comments = relationship("Comments", back_populates="user")
    reactions = relationship("Reactions", back_populates="user")
    followers = relationship("Follows", foreign_keys="[Follows.user_id]")
    following = relationship("Follows", foreign_keys="[Follows.follower_id]")


class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    tagged_user = Column(String)
    created_by = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(
        DateTime, default=datetime.now(timezone.utc), server_defasult=func.now()
    )

    user = relationship("Users", back_populates="posts")
    comments = relationship("Comments", back_populates="post")
    reactions = relationship("Reactions", back_populates="post")

    def set_tagged_user(self, users: list):
        self.tagged_user = json.dumps(users)

    def get_tagged_user(self):
        if self.tagged_user is None:
            return []
        return json.loads(self.tagged_user)

    def is_user_tagged(self, username: str):
        if not self.tagged_user:
            return False

        try:
            tagged_users = json.loads(self.tagged_user)
        except json.JSONDecodeError:
            return False

        return username in tagged_users


class Comments(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("Users", back_populates="comments")
    post = relationship("Posts", back_populates="comments")
    reactions = relationship("Reactions", back_populates="comments")


class Reactions(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"))
    comment_id = Column(Integer, ForeignKey("comments.id"))
    reaction_type = Column(SQLAEnum(ReactionType), nullable=False)

    user = relationship("Users", back_populates="reactions")
    post = relationship("Posts", back_populates="reactions")
    comments = relationship("Comments", back_populates="reactions")


class Follows(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    follower_id = Column(Integer, ForeignKey("users.id"))
    following_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("Users", foreign_keys=[user_id], back_populates="followers")
    follower_user = relationship("Users", foreign_keys=[follower_id])
    followed_user = relationship("Users", foreign_keys=[user_id])

    __table_args__ = (UniqueConstraint("user_id", "follower_id", name="unique_follow"),)
