from fastapi import APIRouter, HTTPException, Path
from starlette import status
from database import db_dependency
from .users import user_dependency
from models import Posts, Reactions
from constants import ReactionType
from schemes import Reaction, ReactionResponse
from sqlalchemy.orm import joinedload

router = APIRouter()


@router.post("/{post_id}/reactions", status_code=status.HTTP_201_CREATED, response_model=ReactionResponse)
async def add_reaction_to_post(
    user: user_dependency, db: db_dependency, reaction_request: Reaction,post_id: int = Path(gt=0)
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post_model = db.query(Posts).filter(Posts.id == post_id).first()
    
    if query_post_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
        
    reaction_model = Reactions(
        **reaction_request.model_dump(),
        owner_id = user.get("id"),
        post_id = post_id
    )
    
    db.add(reaction_model)
    db.commit()
    
    return ReactionResponse(
        detail="Reaction added to post",
        post_content=query_post_model.content,
        reaction_type=reaction_model.reaction_type
    )
    
    