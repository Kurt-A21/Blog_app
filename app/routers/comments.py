from fastapi import APIRouter, HTTPException, Path as PathParam
from starlette import status
from datetime import datetime
import pytz
from app.db import db_dependency, Comments, Posts
from .users import user_dependency
from app.schemes import (
    CommentCreate,
    CommentResponse,
    CommentUpdateResponse,
    CommentUpdate,
)
from sqlalchemy.orm import joinedload
from app.utils import is_user_authenticated, get_comment_or_404, get_post_or_404

router = APIRouter()


@router.post(
    "/{post_id}/comment",
    status_code=status.HTTP_201_CREATED,
    response_model=CommentResponse,
)
async def create_comment(
    user: user_dependency,
    db: db_dependency,
    comment_request: CommentCreate,
    post_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)

    comment_model = Comments(
        owner_id=check_auth.get("id"),
        post_id=post_id,
        content=comment_request.comment_content,
        created_at=datetime.now(pytz.utc),
    )

    db.add(comment_model)
    db.commit()

    return CommentResponse(
        detail="Comment added successully",
        post_id=query_post.id,
        post_content=query_post.content,
        comment_id=comment_model.id,
        comment_content=comment_model.content,
        created_at=comment_model.created_at,
    )


@router.put(
    "/{post_id}/comment/{comment_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommentUpdateResponse,
)
async def update_comment(
    user: user_dependency,
    db: db_dependency,
    update_comment_request: CommentUpdate,
    post_id: int = PathParam(gt=0),
    comment_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    get_post_or_404(db=db, post_id=post_id)
    query_comment = get_comment_or_404(db=db, comment_id=comment_id)

    if query_comment.owner_id != check_auth.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to update this comment",
        )

    query_comment.content = update_comment_request.comment_content
    query_comment.updated_date = datetime.now(pytz.utc)

    db.add(query_comment)
    db.commit()

    return CommentUpdateResponse(
        detail="Comment updated successfully",
        comment_content=query_comment.content,
        updated_date=query_comment.updated_date,
    )


@router.delete("/{post_id}/comment/{comment_id}", status_code=status.HTTP_200_OK)
async def delete_comment(
    user: user_dependency,
    db: db_dependency,
    post_id: int = PathParam(gt=0),
    comment_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    query_post = (
        db.query(Posts)
        .options(joinedload(Posts.comments))
        .filter(Posts.id == post_id)
        .first()
    )

    query_comment = next(
        (comment for comment in query_post.comments if comment.id == comment_id),
        None,
    )

    if not query_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if query_comment.owner_id != check_auth.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to update this comment",
        )

    db.delete(query_comment)
    db.commit()
    return {"detail": "Comment deleted succcessfully"}
