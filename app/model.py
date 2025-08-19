from pydantic import BaseModel, EmailStr
from typing import Literal,Optional

class RegisterUser(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: Literal["admin", "consumer"] = "user"

class Token(BaseModel):
    access_token: str
    token_type: str
class Movies(BaseModel):
    moviename: str
    moviedesc: str
    moviegenre: str
    movieyear: int
    available: Optional[bool] = True
   
class MovieResponse(Movies):
    movie_id: int
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

class MovieSucess(BaseModel):
    message:str
class RentalResponse(BaseModel):
    movie_id: int
    moviename: str
    rented_by: str
    rented_on: str
    return_date: Optional[str] = None