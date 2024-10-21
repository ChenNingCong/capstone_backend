from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from typing import Optional
from passlib.context import CryptContext
from pydantic import BaseModel

from sqlmodel import Session
from db.model.user import User, get_user
from db.init import SessionDep
from sqlmodel import select


router = APIRouter()

# password hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# This is unsafe, we should store the secret key in a config file
# but I am lazy here...
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None


def authenticate_user(session : Session, username: str, password: str) -> Optional[User]:
    user = get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
    
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"expire": expire.isoformat()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/api/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session : SessionDep
) :
    # OAuth2PasswordRequestForm uses username, which is email in our system
    email = form_data.username
    password = form_data.password
    user = authenticate_user(session, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"email": email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session : SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        expire = payload.get("expire")
        if datetime.fromisoformat(expire) < datetime.now(timezone.utc):
            raise  HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The credential has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(session, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@router.get("/api/user/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

# sign in page
@router.post("/api/register")
def create_new_user(email : str, password : str, username : str, session : SessionDep):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if len(username) > 255:
        raise HTTPException(status_code=400, detail="Username is too long")
    if len(email) > 255:
        raise HTTPException(status_code=400, detail="Email is too long")
    statement = select(User).where(User.email == email)
    result = session.exec(statement)
    if result.first() is not None:
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(id = None, username = username, email = email, hashed_password = get_password_hash(password))
    session.add(user)
    session.commit()
    session.refresh(user)
