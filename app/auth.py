from fastapi import FastAPI,HTTPException,Depends,status
from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime, timedelta,timezone
from .database import db,collection
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, MONGO_URI, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# hash the user password 
def hash_password(password: str):
    return pwd_context.hash(password)

# verify password enter by the user with hashed password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# find username
def get_user(db, username: str):
    return db["users"].find_one({"username": username})
    
# user authentication
async def authenticate_user(username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user
# helps in token generation
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# current active user details 
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username") 
        if username is None:
            raise credentials_exception

        user = collection.find_one({"username": username})
        if user is None:
            raise credentials_exception

        return {
            "username": user["username"],
            "role": user["role"]
        }

    except JWTError:
        raise credentials_exception
