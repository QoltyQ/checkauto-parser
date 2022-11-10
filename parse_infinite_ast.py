import conf
import urllib3
import random
import time
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from db_utils import car_to_db
from parse import Parser, get_date, get_advertisement

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## ASTANA

class InfiniteParser(Parser):
    def start_infinite_parsing(self, url: str, city: str, start_page: int):
        while True:
            print(f'[Infinite Parser]: Started infinite parsing at {str(datetime.now())}',flush=True)
            self.mobile_site_infinite(url, city, start_page)
            print(f'[Infinite Parser]: Finished infinite parsing at {str(datetime.now())}',flush=True)

    def mobile_site_infinite(self, url: str, city: str, start_page: int):
        count_cars_in_db = 0
        page = start_page
        while True:
            self.get_proxy()
            if page != 1:
                if page <= 1000:
                    r = self.make_request(conf.MOBILE_URL + url + str(page))
                else: 
                    break
            else:
                r = self.make_request(conf.MOBILE_URL + '/cars/astana/')
            soup = BeautifulSoup(r.text, 'lxml')
            divs_car = soup.select('div[class*="search-list__item"]')
            if not divs_car or (page != 1 and int(soup.find('h1').text.split(' ')[-1]) != page):
                break
            print('page: ' + str(page), flush=True)
            page += 1
            if count_cars_in_db >= 50:
                return page
            for div in divs_car:
                if div is None:
                    break
                if div.get('data-id') is not None:    
                    car_id = div.get('data-id')
                else: 
                    continue
                a = div.find('a', class_='a-card__link')
                adYellow = div.find('div', class_='a-card--pay-yellow')
                adBlue = div.find('div', class_='a-card--pay-yellow')
                advertisement = 'yellow' if adYellow is not None else'blue' if adBlue is not None else 0 
                footer = div.find('div', class_="a-card-footer")
                likes, views = self.parse_likes(footer.find_all('span'))
                temp = likes and likes.text.strip() or 0
                tempv = views and views.text.strip() or 0
                date_of_publication = footer.find('div').text.strip()
                if a is not None and date_of_publication is not None:
                    is_in_database = self.parse_car(car_id, advertisement, date_of_publication, a.get('href'), temp, tempv)
                if is_in_database:
                    count_cars_in_db += 1
                else:
                    count_cars_in_db = 0
            start_page = page
    
    def parse_car(self, car_id: str, advertisement, date_of_publication, link: str, likes):
        count_error = 0
        while True:
            try:
                r = self.make_request(conf.MAIN_URL + link)
                soup = BeautifulSoup(r.text, 'lxml')
                brand, model = self.parse_brand_model(soup.find('div', class_='offer__breadcrumps'))
                year = int(soup.find('h1', class_='offer__title').find('span', class_='year').text.strip())
                price = soup.find('div', class_='offer__price').text.strip().replace('\n   ', '')
                description = self.parse_description(soup.find('div', class_='offer__description'))
                spec_dict = self.parse_specifications(soup.find('div', class_='offer__parameters'))
                author = self.get_author(soup)
                phone = self.get_phone(car_id, referer=link)
                date_of_publication_db = get_date(date_of_publication)
                views = views and int(views) or 0
                likes = likes and int(likes) or 0
                generation = self.parse_generation(soup.find_all('dl'))
                status = 1
                is_in_database = car_to_db(car_id, spec_dict['city'], advertisement, brand, model, year, generation, likes,
                                           spec_dict['condition'],
                                           spec_dict['availability'], spec_dict['car_body'],
                                           spec_dict['engine_volume'], spec_dict['mileage'], spec_dict['transmission'],
                                           spec_dict['steering_wheel'], spec_dict['color'], spec_dict['drive'],
                                           spec_dict['customs_cleared'], author, phone, views, 0, description,
                                           price,
                                           date_of_publication_db, status)
                if not is_in_database:
                    print(f'{car_id} added to db',flush=True)
                else:
                    print(f'{car_id} is already in db',flush=True)
                return is_in_database
            except:
                count_error += 1
                if count_error >= 5:
                    return True


if __name__ == '__main__':
    print('Parsing Started!',flush=True)
    p = InfiniteParser()
    city = 'astana'
    url, name = conf.cities_dict[city]
    p.start_infinite_parsing(url, name, 1)
