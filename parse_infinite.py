from asyncio.windows_events import NULL
from this import d
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


class InfiniteParser(Parser):
    def start_infinite_parsing(self, url: str, city: str, start_page: int):
        while True:
            print(f'[Infinite Parser]: Started infinite parsing at {str(datetime.now())}')
            self.mobile_site_infinite(url, city, start_page)
            print(f'[Infinite Parser]: Finished infinite parsing at {str(datetime.now())}')

    def cars_links(self, url: str, city: str, start_page: int):
        count_cars_in_db = 0
        page = start_page
        while True:
            if page != 1:
                r = self.make_request(conf.MAIN_URL + url + str(page))
                rr = self.make_request(conf.MOBILE_URL + url + str(page))
            else:
                r = self.make_request(conf.MAIN_URL + '/cars/almaty/')
                rr = self.make_request(conf.MOBILE_URL + '/cars/almaty/')
            soup = BeautifulSoup(r.text, 'lxml')
            divs_car = soup.select('div[class*="a-list__item"]')
            if not divs_car or (page != 1 and int(soup.find('h1').text.split(' ')[-1]) != page):
                break
            page += 1
            if count_cars_in_db >= 50:
                return page
            for div in divs_car:
                if div is None:
                    break
                sec = random.randint(3,6)
                time.sleep(sec)
                carId = div.find('div', class_='a-card')
                if carId is not None:
                    car_id = carId.get('data-id')
                else:
                    continue
                a = div.find('a', class_='a-card__link')
                adYellow = div.find('div', class_='a-card--pay-yellow')
                adBlue = div.find('div', class_='a-card--pay-yellow')
                if adYellow is not None:
                    advertisement = 'yellow'
                if adBlue is not None:
                    advertisement = 'blue'
                else: 
                    advertisement = NULL
                date_of_publication = div.find('span', class_='a-card__param--date')
                likes = div.find('span', class_="fi-like")
                if a is not None and date_of_publication is not None:
                    is_in_database = self.parse_car(car_id, advertisement, date_of_publication.text, a.get('href'))
                if is_in_database:
                    count_cars_in_db += 1
                else:
                    count_cars_in_db = 0
            print('page: ' + str(page))
    
    def mobile_site_infinite(self, url: str, city: str, start_page: int):
        count_cars_in_db = 0
        page = start_page
        print(page, '------------------------', start_page)
        while True:
            if page != 1:
                r = self.make_request(conf.MOBILE_URL + url + str(page))
            else:
                r = self.make_request(conf.MOBILE_URL + '/cars/almaty/')
            soup = BeautifulSoup(r.text, 'lxml')
            divs_car = soup.select('div[class*="search-list__item"]')
            if not divs_car or (page != 1 and int(soup.find('h1').text.split(' ')[-1]) != page):
                break
            page += 1
            if count_cars_in_db >= 100000:
                return page
            for div in divs_car:
                if div is None:
                    break
                sec = random.randint(1,3)
                time.sleep(sec)
                if div.get('data-id') is not None:    
                    car_id = div.get('data-id')
                else: 
                    continue
                print(car_id)
                a = div.find('a', class_='a-card__link')
                adYellow = div.find('div', class_='a-card--pay-yellow')
                adBlue = div.find('div', class_='a-card--pay-yellow')
                if adYellow is not None:
                    advertisement = 'yellow'
                if adBlue is not None:
                    advertisement = 'blue'
                else: 
                    advertisement = NULL
                footer = div.find('div', class_="a-card-footer")
                likes = self.parse_likes(footer.find_all('span'))
                print(likes,"likes")
                if likes:
                    temp = likes.text.strip()
                    print(temp)
                    print(likes.text.strip(), "TEXT")
                else: 
                    temp = 0
                date_of_publication = footer.find('div').text.strip()
                if a is not None and date_of_publication is not None:
                    is_in_database = self.parse_car(car_id, advertisement, date_of_publication, a.get('href'), temp)
                else:
                    print("noneww",a,"korgw",date_of_publication,)
                if is_in_database:
                    count_cars_in_db += 1
                else:
                    count_cars_in_db = 0
            print('page: ' + str(page))
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
                views, phone_views = self.parse_views(car_id)
                if likes:
                    likes = int(likes)
                else:
                    likes = 0
                generation = self.parse_generation(soup.find_all('dl'))
                status = 1
                is_in_database = car_to_db(car_id, spec_dict['city'], advertisement, brand, model, year, generation, likes,
                                           spec_dict['condition'],
                                           spec_dict['availability'], spec_dict['car_body'],
                                           spec_dict['engine_volume'], spec_dict['mileage'], spec_dict['transmission'],
                                           spec_dict['steering_wheel'], spec_dict['color'], spec_dict['drive'],
                                           spec_dict['customs_cleared'], author, phone, views, phone_views, description,
                                           price,
                                           date_of_publication_db, status)
                if not is_in_database:
                    print(f'{car_id} added to db')
                else:
                    print(f'{car_id} is already in db')
                return is_in_database
            except:
                count_error += 1
                if count_error >= 5:
                    return True


if __name__ == '__main__':
    print('Parsing Started!')
    p = InfiniteParser()
    city = 'almaty'
    url, name = conf.cities_dict[city]
    p.start_infinite_parsing(url, name, 1)
