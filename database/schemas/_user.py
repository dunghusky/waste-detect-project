from pydantic import BaseModel

class Login(BaseModel):
    user_name: str
    password: str

class UserDelete(BaseModel):
    idUser: int
