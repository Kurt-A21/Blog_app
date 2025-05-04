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
    avatar = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    role = Column(SQLAEnum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=True)

    posts = relationship("Posts", back_populates="user", cascade="all, delete-orphan")
    comments = relationship(
        "Comments", back_populates="user", cascade="all, delete-orphan"
    )
    reply = relationship(
        "CommentReply", back_populates="user", cascade="all, delete-orphan"
    )
    reactions = relationship(
        "Reactions", back_populates="user", cascade="all, delete-orphan"
    )
    followers = relationship(
        "Follows", foreign_keys="[Follows.user_id]", cascade="all, delete-orphan"
    )
    following = relationship(
        "Follows", foreign_keys="[Follows.follower_id]", cascade="all, delete-orphan"
    )


class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    tagged_user = Column(String)
    created_by = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_date = Column(DateTime, nullable=True)

    user = relationship("Users", back_populates="posts")
    comments = relationship(
        "Comments", back_populates="post", cascade="all, delete-orphan"
    )
    reply = relationship(
        "CommentReply", back_populates="post", cascade="all, delete-orphan"
    )
    reactions = relationship(
        "Reactions", back_populates="post", cascade="all, delete-orphan"
    )

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
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    post_id = Column(
        Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_date = Column(DateTime, nullable=True)

    user = relationship("Users", back_populates="comments")
    post = relationship("Posts", back_populates="comments")
    replies = relationship(
        "CommentReply", back_populates="comment", cascade="all, delete-orphan"
    )
    reactions = relationship(
        "Reactions", back_populates="comments", cascade="all, delete-orphan"
    )


class CommentReply(Base):
    __tablename__ = "comment_replies"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    post_id = Column(
        Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    comment_id = Column(
        Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_date = Column(DateTime, nullable=True)

    user = relationship("Users", back_populates="reply")
    post = relationship("Posts", back_populates="reply")
    comment = relationship("Comments", back_populates="replies")
    reactions = relationship(
        "Reactions", back_populates="reply", cascade="all, delete-orphan"
    )


class Reactions(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"))
    reply_id = Column(Integer, ForeignKey("comment_replies.id", ondelete="CASCADE"))
    reaction_type = Column(SQLAEnum(ReactionType), nullable=False)

    user = relationship("Users", back_populates="reactions")
    post = relationship("Posts", back_populates="reactions")
    comments = relationship("Comments", back_populates="reactions")
    reply = relationship("CommentReply", back_populates="reactions")


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
