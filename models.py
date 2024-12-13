from pydantic import BaseModel, EmailStr

class IPost(BaseModel):
    title: str 
    content: str 
    user_id: int  

class IUser(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        orm_mode = True  # Enable ORM compatibility

class IUserCreate(IUser):
    password: str

class IUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    posts: list[IPost]

    class Config:
        orm_mode = True

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(LoginRequest):
    username: str
    email: EmailStr
    password: str


class IPostCreate(IPost):
    pass
