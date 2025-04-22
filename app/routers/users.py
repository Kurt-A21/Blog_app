from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from database import db_dependency
from models import Users, Follows
from schemes import (
    UserUpdate,
    UserEmailUpdate,
    GetUserResponse,
)
from typing import Annotated, List
from .auth import get_current_user
from sqlalchemy.orm import joinedload

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[GetUserResponse])
async def get_users(db: db_dependency):

    get_user_model = (
        db.query(Users)
        .options(
            joinedload(Users.followers).joinedload(Follows.follower_user),
            joinedload(Users.following).joinedload(Follows.followed_user),
        )
        .all()
    )

    if not get_user_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found"
        )

    for user in get_user_model:
        print(f"\n{user.username}")
        print("Followers:")
        for f in user.followers:
            print("  ➤", f.follower_user.username if f.follower_user else "None")
        print("Following:")
        for f in user.following:
            print("  ➤", f.followed_user.username if f.followed_user else "None")

    return [
        GetUserResponse(
            id=user.id,
            username=user.username,
            bio=user.bio,
            avatar=user.avatar,
            followers=len([f for f in user.followers if f.follower_user]),
            following=len([f for f in user.following if f.followed_user]),
            is_active=user.is_active,
        )
        for user in get_user_model
    ]


@router.get("", status_code=status.HTTP_200_OK)
async def get_current_user_details(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    get_user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    return get_user_model


@router.put("/update_user", status_code=status.HTTP_200_OK)
async def update_user(
    user: user_dependency,
    db: db_dependency,
    update_user_request: UserUpdate,
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    user_details = db.query(Users).filter(Users.id == user.get("id")).first()

    if not user_details:
        raise HTTPException(status_code=404, detail="User not found")

    user_details.username = update_user_request.username
    user_details.bio = update_user_request.bio
    user_details.avatar = update_user_request.avatar

    db.add(user_details)
    db.commit()
    return {"detail": "User updated successfully"}


@router.put("/update_email", status_code=status.HTTP_200_OK)
async def update_user_email(
    user: user_dependency, db: db_dependency, update_email_request: UserEmailUpdate
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    user_details = db.query(Users).filter(Users.id == user.get("id")).first()

    if not user_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_details.email = update_email_request.email

    db.add(user_details)
    db.commit()
    return {"detail": "User email updated successfully"}


@router.delete("/delete_user", status_code=status.HTTP_200_OK)
async def delete_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    db.query(Users).filter(Users.id == user.get("id")).delete()
    db.commit()

    return {"detail": "User deleted successfully"}
