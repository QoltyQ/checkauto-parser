import conf
import urllib3
from random import randint
import time
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from db_utils import get_inserted_cars, car_to_db
from parse import Parser, get_date

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class InfiniteParser(Parser):
    def start_infinite_parsing(self, url: str, city: str):
        while True:
            print(
                f'[Infinite Parser]: Started infinite parsing at {str(datetime.now())}', flush=True)
            self.mobile_site_infinite(url, city)
            print(
                f'[Infinite Parser]: Finished infinite parsing at {str(datetime.now())}', flush=True)
            time.sleep(randint(130, 300))

    def mobile_site_infinite(self, url: str, city: str):
        count_cars_in_db = 0
        while True:
            db_cars = get_inserted_cars()
            batch_of_cars = randint(1, 5)
            for car in db_cars:
                car_id = car.id
                self.parse_car(
                    car_id, f'/a/show/{car_id}', car.advertisement, car.likes, car.date_of_publication)
                batch_of_cars -= 1
                if batch_of_cars == 0:
                    batch_of_cars = randint(1, 5)
                    time.sleep(randint(3, 10))
            break

    def parse_car(self, car_id: str, link: str, advertisement, likes, date_of_publication):
        count_error = 0
        while True:
            try:
                r = self.get_proxy(conf.MAIN_URL + link)
                soup = BeautifulSoup(r.text, 'lxml')
                brand, model = self.parse_brand_model(
                    soup.find('div', class_='offer__breadcrumps'))
                year = int(soup.find('h1', class_='offer__title').find(
                    'span', class_='year').text.strip())
                price = soup.find(
                    'div', class_='offer__price').text.strip().replace('\n   ', '')
                description = self.parse_description(
                    soup.find('div', class_='offer__description'))
                spec_dict = self.parse_specifications(
                    soup.find('div', class_='offer__parameters'))
                author = self.get_author(soup)
                phone = self.get_phone(car_id, referer=link)
                generation = self.parse_generation(soup.find_all('dl'))
                status = 1
                is_in_database = car_to_db(car_id, spec_dict['city'], advertisement, brand, model, year, generation, likes,
                                           spec_dict['condition'],
                                           spec_dict['availability'], spec_dict['car_body'],
                                           spec_dict['engine_volume'], spec_dict['mileage'], spec_dict['transmission'],
                                           spec_dict['steering_wheel'], spec_dict['color'], spec_dict['drive'],
                                           spec_dict['customs_cleared'], author, phone, 0, 0, description,
                                           price, date_of_publication, status)
                if is_in_database:
                    print(f'{car_id} is updated', flush=True)
                return is_in_database
            except Exception as e:
                print(e)
                count_error += 1
                if count_error >= 5:
                    return True


if __name__ == '__main__':
    print('Parsing Started!', flush=True)
    p = InfiniteParser()
    city = 'almaty'
    url, name = conf.cities_dict[city]
    p.start_infinite_parsing(url, name)
