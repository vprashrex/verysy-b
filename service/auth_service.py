import base64
from datetime import datetime
from uuid import uuid4
from fastapi import HTTPException
import passlib.hash as _hash


'''
/// SCHEMA ///
'''
from pydantic import BaseModel

class LoginSchema(BaseModel):
    email: str
    password: str

class ForgotPasswordSchema(BaseModel):
    email: str
    new_password: str


class AuthService:

    @staticmethod
    async def login_service(login:LoginSchema):
        