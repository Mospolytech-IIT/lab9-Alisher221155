from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..db import SessionLocal, Post

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic модели для запросов
class PostCreate(BaseModel):
    title: str
    content: str
    user_id: int

# CRUD для Posts
@router.post("/", response_model=dict)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(title=post.title, content=post.content, user_id=post.user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return {"message": f"Post '{db_post.title}' created successfully!"}

@router.get("/", response_model=list)
def list_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()

@router.get("/user/{user_id}/", response_model=list)
def list_posts_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Post).filter(Post.user_id == user_id).all()

@router.put("/{post_id}/", response_model=dict)
def update_post(post_id: int, post: PostCreate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db_post.title = post.title
    db_post.content = post.content
    db.commit()
    return {"message": f"Post '{db_post.title}' updated successfully!"}

@router.delete("/{post_id}/", response_model=dict)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"message": f"Post '{db_post.title}' deleted successfully!"}
