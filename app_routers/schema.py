from fastapi import HTTPException
import logging
import re
from typing import TypeVar,Optional
from pydantic import BaseModel,validator
from sqlalchemy import false

T = TypeVar('T')

#get root logger
logger = logging.getLogger(__name__)

class LoginSchema(BaseModel):
    email: str
    password: str

class ResponseSchema(BaseModel):
    detail: str
    result: Optional[T] = None

class ForgotPasswordSchema(BaseModel):
    email: str
    new_password: str