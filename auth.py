from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..db import SessionLocal, User
from ..models import RegisterRequest, LoginRequest, IUser

# Initialize router and database
router = APIRouter()

# JWT Configuration
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions for JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# Routes
@router.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    print(user.username)
    stored_user: IUser = db.query(User).filter(User.username == user.username).first()
    
    if not stored_user:
        raise HTTPException(status_code=401, detail="User not found")
    if not pwd_context.verify(user.password, stored_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "message": "Токен получен"}

@router.post("/register")
def register(user: RegisterRequest, db: Session = Depends(get_db)):
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    
    # Create SQLAlchemy user object
    new_user = User(username=user.username, email=user.email, password=hashed_password)
    
    # Add the user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return the created user (excluding sensitive fields)
    return new_user

@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}! This is a protected route."}
