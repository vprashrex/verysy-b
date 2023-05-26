''' from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_access.models import Influencer

session_maker = sessionmaker(bind=create_engine("sqlite:///models.db"))

with session_maker() as session:
    influnces = session.query(Influencer).all()

    for influence in influnces:
        print(influence.dict()) '''

''' from app_routers.repository import user_repo

r = user_repo.UserRepository()
r.get_email("vprashant5050@gmail.com") '''

from typing import TypeVar,Optional
from pydantic import BaseModel
from data_access.models import Influencer
from app_routers.repository.auth_repo import JWTRepo


T = TypeVar('T')

class ResponseSchema(BaseModel):
    detail: str
    result: Optional[T] = None


d = {
    "id":12211212,
    "full_name":"Prashant",
    "email":"vprashant5050@gmail.com",
    "password":"Prash@5050",
    "about":"nil"
}

''' data = {}
for k,v in d.items():
    if k == "password":
        pass
    else:
        

print(data) '''

''' data = {}
data["sub"] = {k:v  for (k,v) in d.items() if k != "password" and k != "full_name"}
print(data)
'''

SECRET_KEY = "bb7fe48736386c366df3f30cc739edf1b13cbf740633298219cc451f81ace0bf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


from jose import jwt
from typing import Optional
from datetime import timedelta,datetime


class JWTRepo:
    
    def __init__(self,data: dict = {},token: str = None):
        self.data = data
        self.token = token

    def generate_token(self,expires_delta: Optional[timedelta] = None):
        to_encode = self.data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=15)

        to_encode.update({"exp":expire})

        encode_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
        return encode_jwt

    def decode_token(self):
        try:
            decode_token = jwt.decode(
                self.token,SECRET_KEY,algorithms=[ALGORITHM]
            )
            return decode_token if decode_token["expires"] >= datetime.time() else None

        except Exception as e:
            return {}
        
    @staticmethod
    def extract_token(token:str):
        return jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])


''' r = JWTRepo.extract_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImExNjliZjMzLWJjNjItNDYyYS1iYzJiLTI1MzJjZjE4ZWE4YSIsImZ1bGxfbmFtZSI6InByYXNoYW50IiwiZW1haWwiOiJ2cHJhc2hhbnQ1MDUwQGdtYWlsLmNvbSIsImFib3V0IjoiZGVmYXVsdCIsInVzZXJuYW1lIjoicHJhc2hfcmV4IiwidmVyaWZpZWQiOnRydWUsImxvY2F0aW9uIjoiTm9uZSIsImdlbmRlciI6Ik5vbmUiLCJuaWNoZXMiOiJOb25lIiwiY3Vycl9wYWdlIjoiTm9uZSIsImV4cCI6MTY4MTk2MTYzNn0.OVhIiL3dZ-uKi_PBDSa_Si97c7f_Z8T68Ex7NF5AMxw")
print(r) '''

r = JWTRepo({"user":"praash","password":1234})
print(r.generate_token())
