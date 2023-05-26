from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from data_access.models import Influencer
import status
import numpy as np
from typing import List
from pydantic import EmailStr
from fastapi_mailman import Mail,EmailMessage
from fastapi_mailman.config import ConnectionConfig 
import bcrypt
import passlib.hash as _hash
from app_routers import auth


server = FastAPI()

origins = [
    'https://localhost:8080'
]

server.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers = ["*"]
)

class EmailServer:
    def __init__(self,email:List[EmailStr]):
        self.email = email
        self.session_maker = sessionmaker(bind=create_engine("sqlite:///models.db"))

    def send_otp(self):
        with self.session_maker() as session:
            otps = session.query(Influencer).filter(
                Influencer.email == self.email[0]
            ).first()
            if otps is not None:
                session.query(Influencer).update(
                    {"otp":self.otp_code}
                )
                session.commit()
                
    
    async def sendMail(self):
        conf = ConnectionConfig(
            MAIL_USERNAME="socialblend4150@gmail.com",
            MAIL_PASSWORD="lgxffbqlvunagpan",
            MAIL_BACKEND="smtp",
            MAIL_SERVER="smtp.gmail.com",
            MAIL_PORT=587,
            MAIL_USE_TLS=True,
            MAIL_USE_SSL=False,
            MAIL_DEFAULT_SENDER="socialblend4150@gmail.com"
        )

        mail = Mail(conf)
        self.otp_code = int(np.random.randint(100000,999999))

        message = "YOUR OTP CODE IS {}".format(self.otp_code)
        msg = EmailMessage("this is subject",str(message),to=self.email)
        await msg.send()
        self.send_otp()

        
    async def sendVerification(self):
        await self.sendMail()


class Influencer_data:
    def __init__(self):
        self.session_maker = sessionmaker(bind=create_engine("sqlite:///models.db"))

    
    def add(self,full_name,email,about,username,password):
        self.username = username
        influences = [
            Influencer(
                full_name=full_name,
                email=email,
                about=about,
                username=username,
                password=password,
                verified=False,
                location=None
            )
        ]

        with self.session_maker() as session:
            for influence in influences:
                session.add(influence)
            session.commit()

    def get_id(self):
        with self.session_maker() as session:
            return session.query(Influencer).filter(
                Influencer.username == self.username
            ).first().dict()
           

    def fetch(self):
        with self.session_maker() as session:
            influences = session.query(Influencer).all()
            for influence in influences:
                print(influence.dict())

    def check_email(self,email):
        exist = False
        with self.session_maker() as session:
            email_id = session.query(Influencer).filter(
                Influencer.email == str(email)
            ).first()
            if email_id is not None:
                exist = True
        return exist

    def check_username(self,user_name):
        exist = False
        with self.session_maker() as session:
            username = session.query(Influencer).filter(
                Influencer.username == str(user_name)
            ).first()
            if username is not None:
                exist = True
        return exist

    def delete(self):
        with self.session_maker() as session:
            influences = session.query(Influencer).all()
            for infleunce in influences:
                session.delete(infleunce)
            session.commit()


def PasswordEncoder(password):
    hashed = bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt(14))
    return hashed



@server.post("/api/username",response_class=HTMLResponse)
async def add_user(file:dict):
    try:
        username = file["username"]
        db = Influencer_data()
        username = username.lower()
        exist = db.check_username(username)
        if exist:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "already_exist":True
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "already_exist":False
                }
            )
    except Exception as ex:
        print(ex)
        return JSONResponse(status_code=400,content={"error":str(ex)})


@server.post("/api/influncer_info",response_class=HTMLResponse,status_code=status.HTTP_201_CREATED)
async def add_info(file:dict):
    try:
        name = file["name"]
        email = file["email"].lower()
        username = file["username"]
        password = _hash.bcrypt.hash(file["pass"])
        about = file["about"]
        data_base = Influencer_data()
        # check_email
        email_exist = data_base.check_email(email)
        if email_exist:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "already_exist":True           
                }
            )
        else:
            
            data_base.add(name,email,about,username,password)
            out_id = data_base.get_id()["id"]

            await EmailServer([email]).sendVerification()    ############################

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "already_exist":False,             
                    "id":out_id
                }
            )

    except Exception as ex:
        print(ex)
        return JSONResponse(
            status_code = 400,content={"error":ex}
        )

@server.post("/api/resentEmail")
async def resend_email(file:dict):
    try:
        email = file["email"].lower()
        await EmailServer([email]).sendVerification()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error":e
            }
        )

@server.post("/api/verify_otp")
async def verify_otp(file:dict):
    try:
        session_maker = sessionmaker(bind=create_engine("sqlite:///models.db"))

        email = file["email"]
        otp_code = file["otp"]

        with session_maker() as session:
            otps = session.query(Influencer).filter(
                Influencer.email == email
            ).first()

            if otps is not None:
                otp_code = session.query(Influencer).filter(
                    Influencer.otp == otp_code
                ).first()
                if otp_code is not None:
                    session.query(Influencer).update(
                        {"otp":None}
                    )
                    session.query(Influencer).update(
                        {"verified":True}
                    )
                    session.commit()
                    return JSONResponse(
                        status_code = status.HTTP_200_OK,
                        content={
                            "otp_error":False
                        }
                    )
                else:
                    return JSONResponse(
                        status_code = status.HTTP_200_OK,
                        content={
                            "otp_error":True          ########################
                        }
                    )
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error":e
            }
        )

@server.post("/api/location")
async def location(file:dict):
    try:
        session_maker = sessionmaker(bind=create_engine("sqlite:///models.db"))

        location = file["location"]
        user_id = file["user_id"]
        curr_page = file["curr_page"]
        

        with session_maker() as session:
            userids = session.query(Influencer).filter(
                Influencer.id == user_id
            ).first()

            if userids is not None:
                session.query(Influencer).update(
                    {"location":location}
                )
                session.query(Influencer).update(
                    {"curr_page":curr_page}
                )

                session.commit()
                return JSONResponse(
                    status_code = status.HTTP_200_OK,
                    content={

                    }
                )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error":e
            }
        )

@server.post("/api/gender")
async def gender(file:dict):
    try:
        session_maker = sessionmaker(bind=create_engine("sqlite:///models.db"))

        gender = file["gender"]
        user_id = file["user_id"]
        curr_page = file["curr_page"]

        with session_maker() as session:
            userids = session.query(Influencer).filter(
                Influencer.id == user_id
            ).first()

            if userids is not None:
                session.query(Influencer).update(
                    {"gender":gender}
                )
                session.query(Influencer).update(
                    {"curr_page":curr_page}
                )

                session.commit()
                return JSONResponse(
                    status_code = status.HTTP_200_OK,
                    content={

                    }
                )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error":e
            }
        )

@server.post("/api/niches")
async def niches(file:dict):
    try:
        session_maker = sessionmaker(bind=create_engine("sqlite:///models.db"))

        niches = file["niches"]
        curr_page = file["curr_page"]

        s = []
        for i in niches:
            for k,v in i.items():
                s.append(v)
        
        
        user_id = file["user_id"]

        with session_maker() as session:
            userids = session.query(Influencer).filter(
                Influencer.id == user_id
            ).first()

            if userids is not None:
                session.query(Influencer).update(
                    {"niches":str(s)}
                )
                session.query(Influencer).update(
                    {"curr_page":curr_page}
                )

                session.commit()
                return JSONResponse(
                    status_code = status.HTTP_200_OK,
                    content={

                    }
                )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error":e
            }
        )

class Login:
    def __init__(self,email,password):
        self.email = email
        self.password = password
        
        self.session_maker = sessionmaker(bind=create_engine("sqlite:///models.db"))

    def check_email(self):
        with self.session_maker() as session:
            email_id = session.query(Influencer).filter(
                Influencer.email == str(self.email)
            ).first()

            if email_id is not None:
                return email_id.dict()
        return None

def verify_password(password,hashed_password):
    return _hash.bcrypt.verify(password,hashed_password)

server.include_router(auth.router,tags=['Auth'],prefix='/api/login')

from app_routers import users
server.include_router(users.router,prefix='/api/users',tags=['user'])