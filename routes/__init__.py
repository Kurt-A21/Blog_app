from fastapi import APIRouter
from .posts import router as posts_router

router = APIRouter()

api_version = "api/v1"

router.include_router(posts_router, prefix=f"{api_version}/posts", tags=["posts"])
