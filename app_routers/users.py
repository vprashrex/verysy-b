from fastapi import APIRouter,Depends,Security

SECRET_KEY = "bb7fe48736386c366df3f30cc739edf1b13cbf740633298219cc451f81ace0bf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000


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
            else:
                return credentials.credentials
        
        else:
            raise HTTPException(
                status_code=403, detail={"status": "Forbidden", "message": "Invalid authorization code."}
            )

    @staticmethod
    def verify_jwt(jwt_token:str):
        return True if jwt.decode(jwt_token,SECRET_KEY,algorithms=[ALGORITHM]) is not None else False


router = APIRouter(
    dependencies=[Depends(JWTBearer())]
)

from app_routers.schema import ResponseSchema

@router.get("/",response_model=ResponseSchema)
async def get_user_profile(credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    token = JWTRepo.extract_token(credentials)
    print(token)
    return ResponseSchema(
        detail="Sucessfully fetch data!",
        result=token
    )

