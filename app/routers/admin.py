from fastapi import APIRouter, HTTPException, Query, Path as PathParam
from starlette import status
from app.db import db_dependency, Users, Comments, CommentReply
from .users import user_dependency
from app.schemes import UserResponse
from typing import Optional, List
from uuid import UUID
import os
from app.utils import (
    load_environment,
    is_user_admin,
    get_user_by_id_or_404,
    get_post_or_404,
)

router = APIRouter()

load_environment()
BASE_URL = os.getenv("BASE_URL")


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[UserResponse])
async def get_users_details(user: user_dependency, db: db_dependency):
    is_user_admin(user)

    query_users = db.query(Users).all()

    if not query_users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found"
        )

    return [
        UserResponse(
            id=user.id,
            account_id=user.account_id,
            username=user.username,
            email=user.email,
            bio=user.bio,
            avatar=f"{BASE_URL}/static/{user.avatar or 'avatar.png'}",
            user_type=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_seen,
        )
        for user in query_users
    ]


@router.get(
    "/get_user_by_id/", status_code=status.HTTP_200_OK, response_model=UserResponse
)
async def get_user_by_id_or_accound_id(
    user: user_dependency,
    db: db_dependency,
    user_id: Optional[int] = Query(None),
    account_id: Optional[UUID] = Query(None),
):
    is_user_admin(user)

    if not user_id and not account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one ID (user_id or account_id) must be provided",
        )

    user_query = db.query(Users)

    if user_id:
        user_query = user_query.filter(Users.id == user_id)
    if account_id:
        user_query = user_query.filter(Users.account_id == account_id)

    user = user_query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    avatar_url = f"{BASE_URL}/static/{user.avatar or 'avatar.png'}"

    user_response = UserResponse(
        id=user.id,
        account_id=user.account_id,
        username=user.username,
        email=user.email,
        bio=user.bio,
        avatar=avatar_url,
        user_type=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_seen,
    )

    return user_response


@router.delete("/user/{user_id}/delete_user", status_code=status.HTTP_200_OK)
async def delete_user(
    user: user_dependency, db: db_dependency, user_id: int = PathParam(gt=0)
):
    is_user_admin(user)

    query_user = get_user_by_id_or_404(db=db, user_id=user_id)

    if query_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(query_user)
    db.commit()
    return {"detail": "User deleted successfully"}


@router.delete("/post/{post_id}/delete_post", status_code=status.HTTP_200_OK)
async def delete_post(
    user: user_dependency, db: db_dependency, post_id: int = PathParam(gt=0)
):
    is_user_admin(user)

    query_post = get_post_or_404(db=db, post_id=post_id)

    db.delete(query_post)
    db.commit()

    return {"detail": "Post deleted successfully"}


@router.delete("/post/{post_id}/comment/{comment_id}", status_code=status.HTTP_200_OK)
async def delete_comment(
    user: user_dependency,
    db: db_dependency,
    post_id: int = PathParam(gt=0),
    comment_id: int = PathParam(gt=0),
):
    is_user_admin(user)

    query_comment = (
        db.query(Comments)
        .filter(Comments.id == comment_id, Comments.post_id == post_id)
        .first()
    )

    if not query_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    db.delete(query_comment)
    db.commit()

    return {"detail": "Comment deleted successfully"}


@router.delete(
    "/post/{post_id}/comment/{comment_id}/reply/{reply_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_reply(
    user: user_dependency,
    db: db_dependency,
    post_id: int = PathParam(gt=0),
    comment_id: int = PathParam(gt=0),
    reply_id: int = PathParam(gt=0),
):
    is_user_admin(user)

    query_reply = (
        db.query(CommentReply)
        .filter(
            CommentReply.id == reply_id,
            CommentReply.comment_id == comment_id,
            CommentReply.post_id == post_id,
        )
        .first()
    )

    if not query_reply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reply not found"
        )

    db.delete(query_reply)
    db.commit()

    return {"detail": "Reply deleted successfully"}
