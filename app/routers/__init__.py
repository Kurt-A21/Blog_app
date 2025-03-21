from fastapi import APIRouter
# from .posts import routes as posts_router
from .users import router as users_router

router = APIRouter()

# api_version = "/api/v1"

router.include_router(users_router, prefix="/users", tags=["users"])
# router.include_router(posts_router, prefix=f"{api_version}/posts", tags=["posts"])
