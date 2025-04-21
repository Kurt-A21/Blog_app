from fastapi import APIRouter, HTTPException, Path
from starlette import status
from database import db_dependency
from .users import user_dependency
from models import Users, Follows
from schemes import FollowUser

router = APIRouter()


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

    get_user_model = db.query(Users).filter(Users.id == user_id).first()

    if get_user_model is None:
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

    return FollowUser(detail=f"You are now following {get_user_model.username}")
