from psql import connect_to_psql, PSQL_USER, PSQL_PORT, PSQL_HOST, PSQL_DB, PSQL_PASSWORD
from psql import Base, Car, Proxy
from datetime import datetime
from sqlalchemy import inspect

session, engine = connect_to_psql(
    PSQL_USER, PSQL_PASSWORD, PSQL_DB, PSQL_HOST, PSQL_PORT)
Base.metadata.create_all(engine)


def check_ip(ip):
    in_use = session.query(Proxy).filter(ip == Proxy.ip).first()
    if in_use:
        return False
    return True


def save_connection(id: str, ip: str, port: str):
    p = Proxy()
    p.id = id
    p.ip = ip
    p.port = port
    try:
        session.add(p)
        session.commit()
    except Exception as e:
        print(f'[{str(datetime.now())}] Houston, we have problems: ', e)
        session.rollback()


def car_to_db(car_id: str, city: str, advertisement, brand, model, year, generation, likes, condition, availability, car_body,
              engine_volume, mileage, transmission, steering_wheel, color, drive, customs_cleared, author, phone, views,
              phone_views, description, price, date_of_publication, status) -> bool:
    db_car = session.query(Car).filter(car_id == Car.id).first()
    is_in_database = False
    if not db_car:
        c = Car()
        c.id = car_id
        c.city = city
        c.advertisement = advertisement
        c.brand = brand
        c.model = model
        c.year = year
        c.generation = generation
        c.likes = likes
        c.condition = condition
        c.availability = availability
        c.car_body = car_body
        c.engine_volume = engine_volume
        c.mileage = mileage
        c.transmission = transmission
        c.steering_wheel = steering_wheel
        c.color = color
        c.drive = drive
        c.customs_cleared = customs_cleared
        c.author = author
        c.phone = phone
        c.views = views
        c.phone_views = phone_views
        c.description = description
        c.price = price
        c.date_of_publication = date_of_publication
        c.date_of_adding_to_db = datetime.now()
        c.date_of_editing_in_db = datetime.now()
        c.status = status
        try:
            session.add(c)
            session.commit()
            return is_in_database  # this car is not in db
        except Exception as e:
            print(f'[{str(datetime.now())}] Houston, we have problems ', e)
            session.rollback()
    else:
        db_car.date_of_editing_in_db = datetime.now()
        db_car.city = city
        db_car.advertisement = advertisement
        db_car.brand = brand
        db_car.model = model
        db_car.year = year
        db_car.generation = generation
        db_car.likes = likes
        db_car.condition = condition
        db_car.availability = availability
        db_car.car_body = car_body
        db_car.engine_volume = engine_volume
        db_car.mileage = mileage
        db_car.transmission = transmission
        db_car.steering_wheel = steering_wheel
        db_car.color = color
        db_car.drive = drive
        db_car.customs_cleared = customs_cleared
        db_car.author = author
        db_car.phone = phone
        db_car.views = views
        db_car.phone_views = phone_views
        db_car.description = description
        db_car.price = price
        if (not db_car.date_of_update and db_car.date_of_publication != date_of_publication) or \
                (db_car.date_of_update and db_car.date_of_update != date_of_publication):
            db_car.date_of_update = date_of_publication
            db_car.status = 3
        else:
            is_in_database = True  # this car is in db
        session.commit()
        return is_in_database


def create_new_car(car_id: str, city: str, brand, model, price, year, advertisement, likes, views, date) -> bool:
    db_car = session.query(Car).filter(car_id == Car.id).first()
    if not db_car:
        c = Car()
        c.id = car_id
        c.city = city
        c.brand = brand
        c.model = model
        c.year = year
        c.price = price
        c.views = views
        c.likes = likes
        c.advertisement = advertisement
        c.date_of_publication = date
        c.date_of_adding_to_db = datetime.now()
        c.date_of_editing_in_db = datetime.now()
        try:
            session.add(c)
            session.commit()
            return True  # this car is not in db
        except Exception as e:
            print(f'[{str(datetime.now())}] Houston, we have problems: ', e)
            session.rollback()
    else:
        return False


def change_date_of_editing_in_db(car_id) -> bool:
    db_apartment = session.query(Car).filter(car_id == Car.id).first()
    if not db_apartment:
        return False
    db_apartment.date_of_editing_in_db = datetime.now()
    session.commit()
    return True


def get_inserted_cars() -> list:
    db_cars = session.query(Car).filter(Car.brand == None).order_by(
        Car.date_of_adding_to_db.desc())
    return db_cars


def get_cars(limit, offset) -> list:
    db_cars = session.query(Car).order_by(
        Car.date_of_adding_to_db).limit(limit).offset(offset)
    return db_cars
