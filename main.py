from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.routes import users, auth
from . import crud
from .models import IUserCreate, IPostCreate
from .db import SessionLocal

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend's domain for production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Подключение маршрутов
app.include_router(users.router, prefix="/api/users", tags=["Users"])

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    users = crud.get_users(db)
    posts = crud.get_posts(db)
    return templates.TemplateResponse("index.html", {"request": request, "users": users, "posts": posts})

@app.get("/create_user/", response_class=HTMLResponse)
def create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})


@app.get("/edit_post/{post_id}/", response_class=HTMLResponse)
def edit_post_form(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post not found")
    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post})

@app.get("/edit_user/{user_id}/", response_class=HTMLResponse)
def edit_user_form(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("edit_user.html", {"request": request, "user": user})

@app.post("/edit_post/{post_id}/")
def edit_post(post_id: int, post: IPostCreate, db: Session = Depends(get_db)):
    updated_post = crud.update_post(db, post_id, post)
    return {"message": f"Post {updated_post.title} updated successfully!"}

@app.post("/edit_user/{user_id}/")
def edit_user(user_id: int, user: IUserCreate, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db, user_id, user)
    return {"message": f"User {updated_user.username} updated successfully!"}

@app.get("/delete_user/{user_id}/")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    crud.delete_user(db, user_id)
    return {"message": "User deleted successfully!"}

@app.get("/delete_post/{post_id}/")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    crud.delete_post(db, post_id)
    return {"message": "post deleted successfully!"}

@app.get("/create_post/", response_class=HTMLResponse)
def create_post_form(request: Request):
    return templates.TemplateResponse("create_post.html", {"request": request})

@app.post("/create_post/")
def create_post(post: IPostCreate, db: Session = Depends(get_db)):
    crud.create_post(db, post, post.user_id)
    return {"message": "Post created successfully!"}


