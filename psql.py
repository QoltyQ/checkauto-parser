import os
from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()
PSQL_USER = os.environ.get('POSTGRES_USER', 'check_auto')
PSQL_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'B6d3k9GA')
PSQL_HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
PSQL_DB = os.environ.get('POSTGRES_DB', 'kolesa_full')
PSQL_PORT = os.environ.get('POSTGRES_PORT', '5432')


def connect_to_psql(user: str, password: str, db_name: str, host: str, port):
    url = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
    engine = create_engine(url, client_encoding='utf-8', connect_args={"options": "-c timezone=Asia/Almaty"})
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