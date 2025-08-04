from pydantic import BaseModel, EmailStr
from typing import Literal

class RegisterUser(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: Literal["admin", "consumer"] = "user"

class Token(BaseModel):
    access_token: str
    token_type: str

class Movies(BaseModel):
    movie_id : str
    moviename: str
    moviedesc: str
    moviegenre: str
    movieyear: int