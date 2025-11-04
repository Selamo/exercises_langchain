# 1. engine to connect our db to our python program
# 2. declarative base: Help us to be able to create our database model
# 3. Sessionmaker (help us to be able to talk to oour database)


from sqlalchemy import create_engine,Column,Integer,String,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# connect our db to python program
engine=create_engine("sqlite:///allino.db",echo=True)
# in your create engine pass a connection string
print(f"My engine is {engine}")

Base=declarative_base()
sessionLocal=sessionmaker()

class ModelInfo(Base):
    __tablename__='modelinfo'
    id=Column(Integer, primary_key=True, index=True)
    model_name=Column(String(50), nullable=False)
    prompt=Column(String(300), nullable=False)
    email=Column(String(30), nullable=False, unique=True)

class User(Base):
    __tablename__='user'
    id=Column(Integer, primary_key=True, index=True)
    name=Column(String(40), nullable=False)
    email=Column(String(40), nullable=False, unique=True)
    created_at=Column(DateTime, default=datetime.utcnow)

# print(f" first model is {ModelInfo}")

#Migrate Ou
Base.metadata.create_all(bind=engine)

#Add data to datbase
session=sessionLocal(bind=engine)
try:
    # user1=User(name="Allen",email="allem@gmail.com")
    # user2=User(name="Gad", email="gad@gmail.com")
    user3=User(name="Mbom", email="mbom@gmail.com")
    #Use Session to add data to our db
    session.add_all([user3])
    # commit or save your work
    session.commit()

except Exception as e:
    session.rollback()
    print(f"There was an error adding data")

finally:
    session.close()