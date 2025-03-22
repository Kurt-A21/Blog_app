from fastapi import APIRouter
# from .posts import routes as posts_router
from .users import router as users_router
from .auth import router as auth_router

router = APIRouter()

# api_version = "/api/v1"

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(users_router, prefix="/users", tags=["Users"])
# router.include_router(posts_router, prefix=f"{api_version}/posts", tags=["posts"])
