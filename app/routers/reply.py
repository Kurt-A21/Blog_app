from fastapi import APIRouter, HTTPException, Path
from starlette import status
from datetime import datetime
import pytz
from db import db_dependency, Comments, Posts
from .users import user_dependency
from schemes import GetReplies, ReplyCreate, ReplyResponse, ReplyUpdateResponse
from sqlalchemy.orm import joinedload

router = APIRouter()


@router.post("/{post_id}/comment/{comment_id}/reply", status_code=status.HTTP_200_OK)
async def create_reply(
    user: user_dependency,
    db: db_dependency,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
):
    pass
