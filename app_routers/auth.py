from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import passlib.hash as _hash
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm
from fastapi import APIRouter,Request,Depends
from data_access.models import Influencer
import status


'''
///// DATABASE DECLARATIVE FUNCTION ////
'''

DATABASE_URL = "sqlite:///models.db"
engine = create_engine(DATABASE_URL,connect_args={"check_same_thread":False})
session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = _declarative.declarative_base()

def get_db():
    db = session_maker()
    try:
        yield db
    finally:
        db.close()


'''
/// CORS MIDDLEWARE ///
'''
from starlette.middleware import Middleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

origins = [
    'http://localhost:3000'
]

middleware = [
    Middleware(
        TrustedHostMiddleware,
        allowed_hosts = origins
    ),
    Middleware(HTTPSRedirectMiddleware)
]


'''
///// API_ROUTER FOR AUTHENTICATION //////
'''

router = APIRouter()

def verify_password(password,hashed_password):
    return _hash.bcrypt.verify(password,hashed_password)


from pydantic import BaseModel
from datetime import timedelta,datetime
from jose import jwt
from typing import Optional


SECRET_KEY = "bb7fe48736386c366df3f30cc739edf1b13cbf740633298219cc451f81ace0bf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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


from fastapi import Request,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials

class JWTBearer(HTTPBearer):
    
    def __init__(self,auto_error:bool = True):
        super(JWTBearer,self).__init__(auto_error=auto_error)

    async def __call__(self,request:Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer,self).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403,detail={"status": "Forbidden", "message": "Invalid authentication schema."}
                )
            
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail={"status": "Forbidden", "message": "Invalid token or expired token."}
                )
            
            return credentials.credentials
        
        else:
            raise HTTPException(
                status_code=403, detail={"status": "Forbidden", "message": "Invalid authorization code."}
            )

    @staticmethod
    def verify_jwt(jwt_token:str):
        return True if jwt.decode(jwt_token,SECRET_KEY,algorithms=[ALGORITHM]) is not None else False


from app_routers.schema import LoginSchema

class UserRepository:

    async def find_by_email(email:str,db):
        query = db.query(
            Influencer
        ).filter(Influencer.email == str(email)).first()
        if query is not None:
            return query.dict()
        else:
            None

from typing import TypeVar
T = TypeVar('T')

class ResponseSchema(BaseModel):
    detail:str = None
    result: Optional[T] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[T] = None


class UserRepository:
    @staticmethod
    async def find_by_email(email:str,db):
        query = db.query(Influencer).filter(
            Influencer.email == str(email)
        ).first()
        if query is not None:
            return query.dict()
        else:
            return None


@router.post("/")
async def login(login:LoginSchema,db:_orm.Session=Depends(get_db)):
    try:
        _email_id = await UserRepository.find_by_email(login.email,db)
        if _email_id is not None:
            print(login.password)
            if not verify_password(login.password,_email_id["password"]):
                return JSONResponse(
                    content={
                        "detail":"Invalid Password!"
                    }
                )
            else:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "detail":"Succesful Login!",
                        "result":{
                            "token_type":"Bearer",
                            "access_token":JWTRepo(data={k:v  for (k,v) in _email_id.items() if k != "otp" and k != "password"}).generate_token(timedelta(seconds=15)),
                            
                        }
                    }
                )
        else:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "detail":"Email not found!"
                }
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "error":e
            }
        )
