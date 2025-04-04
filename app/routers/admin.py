from fastapi import APIRouter, HTTPException, Path
from starlette import status
from database import db_dependency
from .users import user_dependency
from models import Users
from constants import UserRole

router = APIRouter()


@router.delete("/delete_user/{user_id}", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None or user.get("user_role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    delete_user_model = db.query(Users).filter(Users.id == user_id).first()

    if delete_user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.query(Users).filter(Users.id == user_id).delete()
    db.commit()
    return {"detail": "User deleted successfully"}
    
