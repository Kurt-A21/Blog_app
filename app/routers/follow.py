from fastapi import APIRouter, HTTPException, Path
from starlette import status
from db import db_dependency, Users, Follows
from .users import user_dependency
from schemes import FollowUser, GetFollower
from typing import List

router = APIRouter()


@router.get(
    "{user_id}/followers",
    status_code=status.HTTP_200_OK,
    response_model=List[GetFollower],
)
async def get_followers(db: db_dependency, user_id: int = Path(gt=0)):
    get_followers = (
        db.query(Users)
        .join(Follows, Follows.follower_id == Users.id)
        .filter(Follows.user_id == user_id)
        .all()
    )

    if not get_followers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No followers found"
        )

    return [
        GetFollower(user_id=follower.id, username=follower.username)
        for follower in get_followers
    ]


@router.get(
    "/{user_id}/following",
    status_code=status.HTTP_200_OK,
    response_model=List[GetFollower],
)
async def get_following(db: db_dependency, user_id: int = Path(gt=0)):
    get_following = (
        db.query(Users)
        .join(Follows, Follows.user_id == Users.id)
        .filter(Follows.follower_id == user_id)
        .all()
    )

    if not get_following:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not following any users yet",
        )

    return [
        GetFollower(user_id=following.id, username=following.username)
        for following in get_following
    ]


@router.post(
    "/{user_id}/follow", status_code=status.HTTP_201_CREATED, response_model=FollowUser
)
async def follow_user(
    db: db_dependency, user: user_dependency, user_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_user = db.query(Users).filter(Users.id == user_id).first()

    if query_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    existing_follow = (
        db.query(Follows)
        .filter(Follows.follower_id == user.get("id"), Follows.user_id == user_id)
        .first()
    )

    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User is already followed"
        )

    follow_model = Follows(
        user_id=user_id, follower_id=user.get("id"), following_id=user_id
    )

    db.add(follow_model)
    db.commit()

    return FollowUser(detail=f"You are now following {query_user.username}")


@router.delete("/{user_id}/unfollow", status_code=status.HTTP_200_OK)
async def unfollow(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_user = db.query(Users).filter(Users.id == user_id).first()

    if query_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    existing_follow = (
        db.query(Follows)
        .filter(Follows.follower_id == user.get("id"), Follows.user_id == user_id)
        .first()
    )

    if not existing_follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not following this user",
        )

    db.query(Follows).filter(
        Follows.follower_id == user.get("id"), Follows.user_id == user_id
    ).delete()
    db.commit()

    return {"detail": f"You have unfollowed {query_user.username}"}
