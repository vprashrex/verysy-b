import uuid
from sqlalchemy import Column,String,Integer,Boolean,ForeignKey
from sqlalchemy.orm import declarative_base,relationship
import passlib.hash as _hash

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())



class Otp(Base):
    __tablename__ = "otp"

    id = Column(String,primary_key=True, default=generate_uuid())
    influencer_id = Column(String,ForeignKey("influencer.id",ondelete='CASCADE'),nullable=False)
    otp = Column(Integer,nullable=True,unique=True)
    verified = Column(Boolean,nullable=False,server_default='False')

    influencer = relationship("Influencer")

    def dict(self):
        return {
            "id": self.id,
            "otp":self.otp,
            "verified":self.verified,
            "influencer_id":self.influencer_id
        }
    
class Influencer(Base):
    __tablename__ = "influencer"

    id = Column(String,primary_key=True,default=generate_uuid)
    full_name = Column(String,nullable=False)
    email = Column(String,nullable=False)
    about = Column(String,nullable=False)
    username = Column(String,nullable=False)
    password = Column(String,nullable=False)
    verified = Column(Boolean,nullable=False,server_default='False')
    otp = Column(Integer,nullable=True)
    
    
    location = Column(String,nullable=True,server_default='None')
    gender = Column(String,nullable=True,server_default="None")
    niches = Column(String,nullable=True,server_default="None")


    curr_page = Column(Integer,nullable=True,server_default="None")


    def dict(self):
        return {
            "id":self.id,
            "full_name":self.full_name,
            "email":self.email,
            "about":self.about,
            "username":self.username,
            "password":self.password,
            "verified":self.verified,
            "otp":self.otp,

            "location":self.location,
            "gender":self.gender,
            "niches":self.niches,

            "curr_page":self.curr_page
        }


class Influencer_data:
    
    def __init__(self):
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine
        self.session_maker = sessionmaker(bind=create_engine("sqlite:///models.db"))

    def add(self,full_name,email,about,username,password):
        influences = [
            Influencer(
                full_name=full_name,
                email=email,
                about=about,
                username=username,
                password=password,
                verified=False
            )
        ]
        with self.session_maker() as session:
            for influence in influences:
                session.add(influence)
            session.commit()

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



if __name__ == '__main__':
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    session_maker = sessionmaker(bind=create_engine("sqlite:///influencer.db"))
    db = Influencer_data()
    db.add("prashant","vprashant5050@gmail.com","Facebook","prashrex","prash@123")
    db.fetch()