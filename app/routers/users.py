from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from db import db_dependency, Users, Follows
from schemes import UserUpdate, UserEmailUpdate, GetUserResponse, UserVerification
from typing import Annotated, List
from .auth import get_current_user, bcrypt_context
from sqlalchemy.orm import joinedload

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("", status_code=status.HTTP_200_OK, response_model=List[GetUserResponse])
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


@router.get("/current_user", status_code=status.HTTP_200_OK)
async def get_current_user_details(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    get_user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    return get_user_model


@router.put("/change_password", status_code=status.HTTP_200_OK)
async def change_password(
    user: user_dependency, db: db_dependency, verify_user: UserVerification
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(verify_user.password, user_model.password):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )

    user_model.password = bcrypt_context.hash(verify_user.new_password)

    db.add(user_model)
    db.commit()

    return {"detail": "Password updated successfully"}


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
