from fastapi import APIRouter, HTTPException, Path
from starlette import status
from db import db_dependency, Posts, Reactions, Comments, CommentReply
from .users import user_dependency
from schemes import Reaction, ReactionResponse

router = APIRouter()


@router.post(
    "/{post_id}/reaction",
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

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    existing_reaction = (
        db.query(Reactions)
        .filter(Reactions.post_id == post_id, Reactions.owner_id == user.get("id"))
        .first()
    )

    if existing_reaction is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already reacted to post",
        )

    reaction_model = Reactions(
        owner_id=user.get("id"),
        post_id=post_id,
        reaction_type=reaction_request.reaction_type,
    )

    db.add(reaction_model)
    db.commit()

    return ReactionResponse(
        detail="Reaction added to post",
        post_content=query_post.content,
        reaction_type=reaction_model.reaction_type,
    )


@router.post(
    "/{post_id}/comment/{comment_id}/reaction",
    status_code=status.HTTP_201_CREATED,
    response_model=ReactionResponse,
)
async def add_reaction_to_comment(
    user: user_dependency,
    db: db_dependency,
    reaction_request: Reaction,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    query_comment = db.query(Comments).filter(Comments.id == comment_id).first()

    if query_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    existing_reaction = (
        db.query(Reactions)
        .filter(
            Reactions.comment_id == comment_id, Reactions.owner_id == user.get("id")
        )
        .first()
    )

    if existing_reaction is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already reacted to comment",
        )

    if query_comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the given post",
        )

    reaction_model = Reactions(
        owner_id=user.get("id"),
        post_id=post_id,
        comment_id=comment_id,
        reaction_type=reaction_request.reaction_type,
    )

    db.add(reaction_model)
    db.commit()

    return ReactionResponse(
        detail="Reaction added to comment",
        post_content=query_post.content,
        comment_content=query_comment.content,
        reaction_type=reaction_model.reaction_type,
    )


@router.post(
    "/{post_id}/comment/{comment_id}/reply/{reply_id}/reaction",
    status_code=status.HTTP_201_CREATED,
    response_model=ReactionResponse,
)
async def add_reaction_to_reply(
    user: user_dependency,
    db: db_dependency,
    reaction_request: Reaction,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
    reply_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    query_post = db.query(Comments).filter(Comments.id == comment_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    query_reaction = db.query(CommentReply).filter(CommentReply.id == reply_id).first()

    if query_reaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reply not found"
        )

    existing_reaction = (
        db.query(Reactions)
        .filter(Reactions.reply_id == reply_id, Reactions.owner_id == user.get("id"))
        .first()
    )

    if existing_reaction is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already reacted to reply",
        )

    if query_reaction.comment_id != comment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reply does not belong to the given comment",
        )

    reaction_model = Reactions(
        owner_id=user.get("id"),
        post_id=post_id,
        comment_id=comment_id,
        reply_id=reply_id,
        reaction_type=reaction_request.reaction_type,
    )

    db.add(reaction_model)
    db.commit()

    return ReactionResponse(
        detail="Reaction added to comment",
        post_content=query_post.content,
        comment_content=query_post.content,
        reply_content=query_reaction.content,
        reaction_type=reaction_model.reaction_type,
    )


@router.put(
    "/{post_id}/reaction/{reaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReactionResponse,
)
async def update_post_reaction(
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

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    query_reaction = db.query(Reactions).filter(Reactions.id == reaction_id).first()

    if not query_reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction to update not found"
        )

    if query_reaction.owner_id != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not authorized to update this reaction",
        )

    query_reaction.reaction_type = update_reaction_request.reaction_type

    db.add(query_reaction)
    db.commit()

    return ReactionResponse(
        detail="Reaction type updated successfully",
        post_content=query_post.content,
        reaction_type=query_reaction.reaction_type,
    )


@router.put(
    "/{post_id}/comment/{comment_id}/reaction/{reaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReactionResponse,
)
async def update_comment_reaction(
    user: user_dependency,
    db: db_dependency,
    update_reaction_request: Reaction,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
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

    query_comment = db.query(Comments).filter(Comments.id == comment_id).first()

    if query_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if query_comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the given post",
        )

    query_reaction = db.query(Reactions).filter(Reactions.id == reaction_id).first()

    if not query_reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction to update not found"
        )

    if query_reaction.owner_id != user.get("id"):
        raise HTTPException(
            status_code=403, detail="Not authorized to update this reaction"
        )

    query_reaction.reaction_type = update_reaction_request.reaction_type

    db.add(query_reaction)
    db.commit()

    return ReactionResponse(
        detail="Reaction type updated successfully",
        post_content=query_post_model.content,
        comment_content=query_comment.content,
        reaction_type=query_reaction.reaction_type,
    )


@router.put(
    "/{post_id}/comment/{comment_id}/reply/{reply_id}/reaction/{reaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReactionResponse,
)
async def update_reply_reaction(
    user: user_dependency,
    db: db_dependency,
    update_reaction_request: Reaction,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
    reply_id: int = Path(gt=0),
    reaction_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    query_comment = db.query(Comments).filter(Comments.id == comment_id).first()

    if query_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if query_comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the given post",
        )

    query_reply = db.query(CommentReply).filter(CommentReply.id == reply_id).first()

    if query_reply is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reply not found"
        )

    if query_reply.comment_id != comment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reply does not belong to the given commentd",
        )

    query_reaction = db.query(Reactions).filter(Reactions.id == reaction_id).first()

    if not query_reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction to update not found"
        )

    if query_reaction.owner_id != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this reaction",
        )

    query_reaction.reaction_type = update_reaction_request.reaction_type

    db.add(query_reaction)
    db.commit()

    return ReactionResponse(
        detail="Reaction type updated successfully",
        post_content=query_post.content,
        comment_content=query_comment.content,
        reply_content=query_reply.content,
        reaction_type=query_reaction.reaction_type,
    )


@router.delete(
    "/{post_id}/reaction/{reaction_id}",
    status_code=status.HTTP_200_OK,
)
async def undo_post_reaction(
    user: user_dependency,
    db: db_dependency,
    post_id: int = Path(gt=0),
    reaction_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    query_reactiom = db.query(Reactions).filter(Reactions.id == reaction_id).first()

    if query_reactiom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction to undo not found"
        )

    if query_reactiom.owner_id != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to undo this reaction",
        )

    db.delete(query_reactiom)
    db.commit()

    return {"detail": "Reaction deleted successfully"}


@router.delete(
    "/{post_id}/comment/{comment_id}/reaction/{reaction_id}",
    status_code=status.HTTP_200_OK,
)
async def undo_comment_reaction(
    user: user_dependency,
    db: db_dependency,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
    reaction_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    query_comment = db.query(Comments).filter(Comments.id == comment_id).first()

    if query_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if query_comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the given post",
        )

    query_reaction = db.query(Reactions).filter(Reactions.id == reaction_id).first()

    if query_reaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction to undo not found"
        )

    if query_reaction.owner_id != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to undo this reaction",
        )

    db.delete(query_reaction)
    db.commit()

    return {"detail": "Reaction deleted successfully"}


@router.delete(
    "/{post_id}/comment/{comment_id}/reply/{reply_id}/reaction/{reaction_id}",
    status_code=status.HTTP_200_OK,
)
async def undo_reply_reaction(
    user: user_dependency,
    db: db_dependency,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
    reply_id: int = Path(gt=0),
    reaction_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    query_comment = db.query(Comments).filter(Comments.id == comment_id).first()

    if query_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if query_comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the given post",
        )

    query_reply = db.query(CommentReply).filter(CommentReply.id == reply_id).first()

    if query_reply is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reply not found"
        )

    if query_reply.comment_id != comment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reply does not belong to the given comment",
        )

    query_reaction = db.query(Reactions).filter(Reactions.id == reaction_id).first()

    if query_reaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction to undo not found"
        )

    if query_reaction.owner_id != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to undo this reaction",
        )

    db.delete(query_reaction)
    db.commit()

    return {"detail": "Reaction deleted successfully"}
