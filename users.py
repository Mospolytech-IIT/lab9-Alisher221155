from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from ..db import SessionLocal, User
from ..models import IUserCreate, IUserResponse 

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD для Users
@router.post("/create/", response_model=dict)
def create_user(user: IUserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email, password=user.password)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"message": f"User {db_user.username} created successfully!"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")

@router.get("/", response_model=list[IUserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/{user_id}/", response_model=IUserResponse)
def list_users(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()

@router.put("/{user_id}/", response_model=dict)
def update_user(user_id: int, user: IUserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = user.username
    db_user.email = user.email
    db_user.password = user.password

    db.commit()
    
    return {"message": f"User {db_user.username} updated successfully!"}

@router.delete("/{user_id}/", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"message": f"User {db_user.username} deleted successfully!"}
