import os
from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv


def configure():
    load_dotenv()


configure()

Base = declarative_base()

PSQL_USER = os.getenv('POSTGRES_USER')
PSQL_PASSWORD = os.getenv('POSTGRES_PASSWORD')
PSQL_HOST = os.getenv('POSTGRES_HOST')
PSQL_DB = os.getenv('POSTGRES_DB')
PSQL_PORT = os.getenv('POSTGRES_PORT')


def connect_to_psql(user: str, password: str, db_name: str, host: str, port):
    url = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
    engine = create_engine(url, client_encoding='utf-8',
                           pool_pre_ping=True, pool_recycle=86400)
    db_session = sessionmaker(bind=engine)
    session = db_session()
    return session, engine


class Car(Base):
    __tablename__ = 'cars'
    id = Column(String(255), primary_key=True)
    city = Column(String(255))
    advertisement = Column(String(255))
    brand = Column(String(255))
    model = Column(String(255))
    year = Column(Integer)
    generation = Column(String(255))
    likes = Column(Integer)
    condition = Column(String(255))
    availability = Column(String(255))
    car_body = Column(String(255))
    engine_volume = Column(String(255))
    mileage = Column(String(255))
    transmission = Column(String(225))
    steering_wheel = Column(String(255))
    color = Column(String(255))
    drive = Column(String(255))
    customs_cleared = Column(String(255))
    author = Column(String(255))
    phone = Column(String(255))
    views = Column(Integer)
    phone_views = Column(Integer)
    description = Column(Text)
    price = Column(String(255))
    date_of_publication = Column(Date)
    date_of_adding_to_db = Column(DateTime)
    date_of_update = Column(Date)
    status = Column(Integer)
    date_of_editing_in_db = Column(DateTime)


class Proxy(Base):
    __tablename__ = 'proxy_ip'
    id = Column(String(255), primary_key=True)
    ip = Column(String(255))
    port = Column(String(255))
