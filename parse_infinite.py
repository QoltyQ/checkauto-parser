import conf
import urllib3
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
            self.cars_links(url, city, start_page)
            print(f'[Infinite Parser]: Finished infinite parsing at {str(datetime.now())}')

    def cars_links(self, url: str, city: str, start_page: int):
        count_cars_in_db = 0
        page = start_page
        while True:
            r = self.make_request(conf.MAIN_URL + url + str(page))
            soup = BeautifulSoup(r.text, 'lxml')
            divs_car = soup.select('div[class*="row vw-item list-item"]')
            if not divs_car or (page != 1 and int(soup.find('h1').text.split(' ')[-1]) != page):
                break
            page += 1
            if count_cars_in_db >= 50:
                return page
            for div in divs_car:
                if div is None:
                    break
                car_id = div.get('data-id')
                a = div.find('a', class_='list-link ddl_product_link')

                advertisement = get_advertisement(div.attrs['class'])

                date_of_publication = div.find('span', class_='date').text.strip()
                is_in_database = self.parse_car(car_id, advertisement, date_of_publication, a.get('href'))
                if is_in_database:
                    count_cars_in_db += 1
                else:
                    count_cars_in_db = 0
            print('page: ' + str(page))

    def parse_car(self, car_id: str, advertisement, date_of_publication, link: str):
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
                status = 1
                is_in_database = car_to_db(car_id, spec_dict['city'], advertisement, brand, model, year,
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
