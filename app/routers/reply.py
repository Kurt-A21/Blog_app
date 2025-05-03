from fastapi import APIRouter, HTTPException, Path
from starlette import status
from datetime import datetime
import pytz
from db import db_dependency, Comments, Posts, CommentReply
from .users import user_dependency
from schemes import ReplyCreate, ReplyResponse, ReplyUpdateResponse
from sqlalchemy.orm import joinedload

router = APIRouter()


@router.post(
    "/{post_id}/comment/{comment_id}/reply", status_code=status.HTTP_201_CREATED
)
async def create_reply(
    user: user_dependency,
    db: db_dependency,
    reply_request: ReplyCreate,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    query_comment = db.query(Comments).filter(Comments.id == comment_id).first()

    if query_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    reply_model = CommentReply(
        owner_id=user.get("id"),
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
        created_at=datetime.now(pytz.utc),
    )


@router.put(
    "/{post_id}/comment/{comment_id}/reply/{reply_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReplyUpdateResponse,
)
async def update_reply(
    user: user_dependency,
    db: db_dependency,
    update_reply_request: ReplyCreate,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
    reply_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    query_comment = db.query(Comments).filter(Comments.id == comment_id).first()

    if query_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    query_reply = db.query(CommentReply).filter(CommentReply.id == reply_id).first()

    if query_reply is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reply not found"
        )

    query_reply.content = update_reply_request.reply_content
    query_reply.updated_date = datetime.now(pytz.utc)

    db.add(query_reply)
    db.commit()

    return ReplyUpdateResponse(
        detail="Reply updated successfully",
        reply_content=query_reply.content,
        updated_date=datetime.now(pytz.utc),
    )


@router.delete(
    "/{post_id}/comment/{comment_id}/reply/{reply_id}", status_code=status.HTTP_200_OK
)
async def delete_reply(
    user: user_dependency,
    db: db_dependency,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
    reply_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

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

    db.delete(query_reply)
    db.commit()

    return {"detail": "Reply deleted successfully"}
