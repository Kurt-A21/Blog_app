from fastapi import APIRouter
from .posts import router as posts_router
from .users import router as users_router
from .auth import router as auth_router
from .admin import router as admin_router
from .comments import router as comment_router
from .reactions import router as reaction_router


router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(admin_router, prefix="/admin", tags=["Admin"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(posts_router, prefix="/posts", tags=["Posts"])
router.include_router(comment_router, prefix="/posts", tags=["Comments"])
router.include_router(reaction_router, prefix="/posts", tags=["Reactions"])
