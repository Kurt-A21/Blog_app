from fastapi import APIRouter, HTTPException, Path
from starlette import status
from database import db_dependency
from .users import user_dependency
from models import Posts, Reactions
from schemes import Reaction, ReactionResponse
from sqlalchemy.orm import joinedload

router = APIRouter()


@router.post(
    "/{post_id}/reactions",
    status_code=status.HTTP_201_CREATED,
    response_model=ReactionResponse,
)
async def add_reaction_to_post(
    user: user_dependency,
    db: db_dependency,
    reaction_request: Reaction,
    post_id: int = Path(gt=0),
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

    query_reaction_model = (
        db.query(Posts)
        .options(joinedload(Posts.reactions).joinedload(Reactions.user))
        .all()
    )

    if query_reaction_model is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already reacted to post",
        )

    reaction_model = Reactions(
        **reaction_request.model_dump(), owner_id=user.get("id"), post_id=post_id
    )

    db.add(reaction_model)
    db.commit()

    return ReactionResponse(
        detail="Reaction added to post",
        post_content=query_post_model.content,
        reaction_type=reaction_model.reaction_type,
    )


@router.put(
    "/{post_id}/reactions/{reaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReactionResponse,
)
async def update_reaction(
    user: user_dependency,
    db: db_dependency,
    update_reaction_request: Reaction,
    post_id: int = Path(gt=0),
    reaction_id: int = Path(gt=0),
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

    check_reaction_owner = (
        db.query(Reactions).filter(Reactions.owner_id == user.get("id")).first()
    )

    if check_reaction_owner:
        print("Is reaction owner")
        print(user.get("id"))

    if check_reaction_owner is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to update this reaction",
        )

    update_reaction_model = (
        db.query(Reactions).filter(Reactions.id == reaction_id).first()
    )

    if not update_reaction_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction to update not found"
        )

    update_reaction_model.reaction_type = update_reaction_request.reaction_type

    db.add(update_reaction_model)
    db.commit()

    return ReactionResponse(
        detail="Reaction type updated successfully",
        post_content=query_post_model.content,
        reaction_type=update_reaction_model.reaction_type,
    )
