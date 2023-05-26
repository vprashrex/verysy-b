from datetime import datetime,timedelta
from typing import Optional
from jose import jwt
from fastapi import Request,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
import sys

SECRET_KEY = "bb7fe48736386c366df3f30cc739edf1b13cbf740633298219cc451f81ace0bf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class JWTRepo:

    def __init__(self,data: dict= {},token:str = None):
        self.data = data
        self.token = token

    def generate_token(self,expires_delta:Optional[timedelta] = None):
        to_encode = self.data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update(
            {'exp':expire}
        )

        encode_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

        return encode_jwt
    
    def decode_token(self):
        try:
            decode_token = jwt.decode(
                self.token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )
            return decode_token if decode_token['expires'] >= datetime.time() else None
        
        except:
            return {}
    
    @staticmethod
    def extract_token(token:str):
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )


class JWTBearer(HTTPBearer):
    
    def __init__(self,auto_error:bool=True):
        super(JWTBearer,self).__init__(auto_error=auto_error)

    async def __call__(self,request:Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer,self).__call__(request)

        if credentials:
            if not credentials.scheme == 'Bearer':
                raise HTTPException(
                    status_code=403,
                    detail={'status':'Forbidden',
                    'message':"Invalid authentication schema."}
                )

    @staticmethod
    def verify_jwt(jwt_token:str):
        return True if jwt.decode(
            jwt_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        ) is not None else False





''' if __name__ == '__main__':
    payload = {
        "email":"vprashant5050@gmail.com",
        "password":"Prash@5050",
        "curr_page":1
    }
    token = JWTRepo(payload).generate_token()
    
    decoded = JWTRepo().extract_token(token)
    print(decoded)


    sys.exit() '''
    