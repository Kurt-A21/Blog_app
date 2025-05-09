from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from starlette import status
from app.db import db_dependency, Users, Follows
from app.schemes import (
    UserUpdate,
    UserEmailUpdate,
    GetUserResponse,
    UserVerification,
    UserResponse,
)
from typing import Annotated, List
from app.services import upload_image, update_image, remove_image
from .auth import get_current_user, bcrypt_context
from sqlalchemy.orm import joinedload
import os
from app.utils import load_environment, is_user_authenticated, get_user

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]

load_environment()
BASE_URL = os.getenv("BASE_URL")


@router.get("", status_code=status.HTTP_200_OK, response_model=List[GetUserResponse])
async def get_users(db: db_dependency):
    query_users = (
        db.query(Users)
        .options(
            joinedload(Users.followers).joinedload(Follows.follower_user),
            joinedload(Users.following).joinedload(Follows.followed_user),
        )
        .all()
    )

    if not query_users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found"
        )

    return [
        GetUserResponse(
            id=user.id,
            username=user.username,
            bio=user.bio,
            avatar=f"{BASE_URL}/static/{user.avatar or 'avatar.png'}",
            followers=len([f for f in user.followers if f.follower_user]),
            following=len([f for f in user.following if f.followed_user]),
            is_active=user.is_active,
        )
        for user in query_users
    ]


@router.get(
    "/current_user", status_code=status.HTTP_200_OK, response_model=UserResponse
)
async def get_current_user_details(user: user_dependency, db: db_dependency):
    is_user_authenticated(user)
    query_user = get_user(db=db, user=user)

    avatar_url = f"{BASE_URL}/static/{query_user.avatar or 'avatar.png'}"

    return UserResponse(
        id=query_user.id,
        account_id=query_user.account_id,
        username=query_user.username,
        email=query_user.email,
        bio=query_user.bio,
        avatar=avatar_url,
        user_type=query_user.role,
        is_active=query_user.is_active,
        created_at=query_user.created_at,
        last_login=query_user.last_seen,
    )


@router.post("/upload_profile_picture", status_code=status.HTTP_200_OK)
async def upload_profile_picture(
    user: user_dependency, db: db_dependency, file: UploadFile = File(...)
):
    is_user_authenticated(user)
    query_user = get_user(db=db, user=user)

    if query_user.avatar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a profile picture",
        )

    image = await upload_image(file)

    query_user.avatar = image
    db.commit()

    return {"detail": "Profile picture uploaded successfully"}


@router.put("/update_profile_picture", status_code=status.HTTP_200_OK)
async def update_profile_picture(
    user: user_dependency, db: db_dependency, file: UploadFile = File(...)
):
    is_user_authenticated(user)
    query_user = get_user(db=db, user=user)

    if query_user.avatar:
        image = await update_image(user=query_user, file=file)

        query_user.avatar = image
        db.commit()

        return {"detail": "Profile picture updated successfully"}


@router.delete("/remove_profile_picture", status_code=status.HTTP_200_OK)
async def remove_profile_picture(user: user_dependency, db: db_dependency):
    is_user_authenticated(user)
    query_user = get_user(db=db, user=user)

    if query_user.avatar is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a profile picture",
        )

    image = remove_image(user=query_user)

    query_user.avatar = image
    db.commit()

    return {"detail": "Profile picture removed successfully"}


@router.put("/change_password", status_code=status.HTTP_200_OK)
async def change_password(
    user: user_dependency, db: db_dependency, verify_user: UserVerification
):
    is_user_authenticated(user)
    query_user = get_user(db=db, user=user)

    if not bcrypt_context.verify(verify_user.password, query_user.password):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )

    query_user.password = bcrypt_context.hash(verify_user.new_password)

    db.add(query_user)
    db.commit()

    return {"detail": "Password updated successfully"}


@router.put("/update_user", status_code=status.HTTP_200_OK)
async def update_user(
    user: user_dependency,
    db: db_dependency,
    update_user_request: UserUpdate,
):
    is_user_authenticated(user)
    query_user = get_user(db=db, user=user)
    
    query_user.username = update_user_request.username
    query_user.bio = update_user_request.bio

    db.add(query_user)
    db.commit()
    return {"detail": "User updated successfully"}


@router.put("/update_email", status_code=status.HTTP_200_OK)
async def update_user_email(
    user: user_dependency, db: db_dependency, update_email_request: UserEmailUpdate
):
    is_user_authenticated(user)
    query_user = get_user(db=db, user=user)

    query_user.email = update_email_request.email

    db.add(query_user)
    db.commit()
    return {"detail": "User email updated successfully"}


@router.delete("/deactivate_account", status_code=status.HTTP_200_OK)
async def deactivate_account(user: user_dependency, db: db_dependency):
    is_user_authenticated(user)
    query_user = get_user(db=db, user=user)

    if query_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    try:
        db.delete(query_user)
        db.commit()
        return {"detail": "User and all related data deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deactivating the account: {str(e)}",
        )
