from fastapi import APIRouter, HTTPException, Path
from starlette import status
from database import db_dependency
from .users import user_dependency
from models import Posts
from schemes import PostCreate, PostResponse

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_post(
    user: user_dependency, db: db_dependency, post_request: PostCreate
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    post_model = Posts(**post_request.model_dump(), id=user.get("id"))

    db.add(post_model)
    db.commit()

    return PostResponse(
        owner_username=user.get("username"),
        content=post_model.content,
        image_url=post_model.image_url,
    )
