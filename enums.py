from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"


class ReactionType(Enum):
    LIKE = "like"
    LOVE = "love"
    HAHA = "haha"
    HATE = "hate"
    SAD = "sad"
