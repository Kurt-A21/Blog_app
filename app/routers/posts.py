from fastapi import APIRouter, HTTPException, Path
from starlette import status
from database import db_dependency
from .users import user_dependency
from models import Posts
from schemes import PostCreate, CreatePostResponse, PostResponse, PostUpdate, GetPosts
from typing import List

router = APIRouter()

@router.get("", status_code=status.HTTP_200_OK)
async def get_all_posts(db: db_dependency):
    get_posts_model = db.query(Posts).all()
    
    if get_posts_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found")
    
    return get_posts_model

@router.get("/user_posts", status_code=status.HTTP_200_OK, response_model=List[PostResponse])
async def get_user_posts(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    get_posts_model = db.query(Posts).filter(Posts.owner_id == user.get("id")).all()

    if not get_posts_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found"
        )

    return [
        PostResponse(
            owner_username=user.get("username"),
            content=post.content,
            image_url=post.image_url,
            created_at=post.created_at
        )
        for post in get_posts_model
    ]


@router.post(
    "/create", status_code=status.HTTP_201_CREATED, response_model=CreatePostResponse
)
async def create_post(
    user: user_dependency, db: db_dependency, post_request: PostCreate
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    post_model = Posts(**post_request.model_dump(), owner_id=user.get("id"))

    db.add(post_model)
    db.commit()

    return {
        "detail": "Post created successfully",
        "post_details": PostResponse(
            owner_username=user.get("username"),
            content=post_model.content,
            image_url=post_model.image_url,
        ),
    }
    
@router.put("/update_post/{posts_id}", status_code=status.HTTP_200_OK)
async def update_post(user: user_dependency, db: db_dependency, post_request: PostUpdate, posts_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )
        
    post = db.query(Posts).filter(Posts.owner_id == user.get("id")).first()
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized to update this post")
    
    update_posts_model = db.query(Posts).filter(Posts.id == posts_id).first()
    
    if not update_posts_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post to update not found")
    
    update_posts_model.content = post_request.content
    update_posts_model.image_url = post_request.image_url
    
    db.add(update_posts_model)
    db.commit()
    
    return {"detail": "Post updated successfully"}
    
    
