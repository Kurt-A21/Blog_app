from fastapi import APIRouter, HTTPException, Path as PathParam
from starlette import status
from datetime import datetime
import pytz
from app.db import db_dependency, CommentReply
from .users import user_dependency
from app.utils import (
    is_user_authenticated,
    get_reply_or_404,
    get_comment_or_404,
    get_post_or_404,
)
from app.schemes import ReplyCreate, ReplyResponse, ReplyUpdateResponse, ReplyUpdate

router = APIRouter()


@router.post(
    "/{post_id}/comment/{comment_id}/reply", status_code=status.HTTP_201_CREATED
)
async def create_reply(
    user: user_dependency,
    db: db_dependency,
    reply_request: ReplyCreate,
    post_id: int = PathParam(gt=0),
    comment_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)
    query_comment = get_comment_or_404(db=db, comment_id=comment_id)

    reply_model = CommentReply(
        owner_id=check_auth.get("id"),
        post_id=post_id,
        comment_id=comment_id,
        content=reply_request.reply_content,
        created_at=datetime.now(pytz.utc),
    )

    db.add(reply_model)
    db.commit()

    return ReplyResponse(
        detail="Reply added successfully",
        post_id=query_post.id,
        post_content=query_post.content,
        comment_id=query_comment.id,
        comment_content=query_comment.content,
        reply_id=reply_model.id,
        reply_content=reply_model.content,
        created_at=reply_model.created_at,
    )


@router.put(
    "/{post_id}/comment/{comment_id}/reply/{reply_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReplyUpdateResponse,
)
async def update_reply(
    user: user_dependency,
    db: db_dependency,
    update_reply_request: ReplyUpdate,
    post_id: int = PathParam(gt=0),
    comment_id: int = PathParam(gt=0),
    reply_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    get_post_or_404(db=db, post_id=post_id)
    get_comment_or_404(db=db, comment_id=comment_id)
    query_reply = get_reply_or_404(db=db, reply_id=reply_id)

    if query_reply.owner_id != check_auth.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this reply",
        )

    query_reply.content = update_reply_request.reply_content
    query_reply.updated_date = datetime.now(pytz.utc)

    db.add(query_reply)
    db.commit()

    return ReplyUpdateResponse(
        detail="Reply updated successfully",
        reply_content=query_reply.content,
        updated_date=query_reply.updated_date,
    )


@router.delete(
    "/{post_id}/comment/{comment_id}/reply/{reply_id}", status_code=status.HTTP_200_OK
)
async def delete_reply(
    user: user_dependency,
    db: db_dependency,
    post_id: int = PathParam(gt=0),
    comment_id: int = PathParam(gt=0),
    reply_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    query_reply = (
        db.query(CommentReply)
        .filter(
            CommentReply.id == reply_id,
            CommentReply.post_id == post_id,
            CommentReply.comment_id == comment_id,
        )
        .first()
    )

    if not query_reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    if query_reply.owner_id != check_auth.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this reply",
        )

    db.delete(query_reply)
    db.commit()

    return {"detail": "Reply deleted successfully"}
