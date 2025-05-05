from fastapi import APIRouter, HTTPException, Path, Query
from starlette import status
from db import db_dependency, Users, Posts, Comments
from .users import user_dependency
from constants import UserRole
from schemes import UserResponse
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import joinedload


router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[UserResponse])
async def get_users_details(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_users = db.query(Users).all()

    if not query_users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found"
        )

    BASE_URL = "http://127.0.0.1:8000"

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

    if user is None or user.get("user_role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

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

    BASE_URL = "http://127.0.0.1:8000"
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
    user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)
):
    if user is None or user.get("user_role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_user = db.query(Users).filter(Users.id == user_id).first()

    if query_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(query_user)
    db.commit()
    return {"detail": "User deleted successfully"}


@router.delete("/post/{post_id}/delete_post", status_code=status.HTTP_200_OK)
async def delete_post(
    user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)
):
    if user is None or user.get("user_role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    db.delete(query_post)
    db.commit()

    return {"detail": "Post deleted successfully"}


@router.delete("/post/{post_id}/comment/{comment_id}", status_code=status.HTTP_200_OK)
async def delete_comment(
    user: user_dependency,
    db: db_dependency,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
):
    if user is None or user.get("user_role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post = (
        db.query(Posts)
        .options(joinedload(Posts.comments))
        .filter(Posts.id == post_id)
        .first()
    )

    for comment in query_post.comments:
        if comment.id == comment_id:
            db.query(Comments).filter(Comments.id == comment_id).delete()
            db.commit()
            return {"detail": "Comment deleted succcessfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
            )
