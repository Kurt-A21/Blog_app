from fastapi import APIRouter, HTTPException, Path
from starlette import status
from database import db_dependency
from .users import user_dependency
from models import Comments, Posts
from schemes import CommentCreate, CommentResponse

router = APIRouter()

@router.post("/{post_id}/comments", status_code=status.HTTP_200_OK, response_model=CommentResponse)
async def create_comment(user: user_dependency, db: db_dependency, comment_request: CommentCreate ,post_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )
    
    query_model = db.query(Posts).filter(Posts.id == post_id).first()
    
    if query_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        
    comment_model = Comments(**comment_request.model_dump(), user_id=user.get("id"),post_id=post_id )
    
    db.add(comment_model)
    db.commit()
    
    return CommentResponse(
        detail = "Comment added successully",
        post_content = query_model.content,
        content = comment_model.content,
        created_at = comment_model.created_at
    )
    
        
    
        

