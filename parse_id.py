import random
import conf
import time
import urllib3
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from db_utils import change_date_of_editing_in_db
from parse import Parser, get_advertisement
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class InfiniteIdParser(Parser):
    def start_infinite_parsing(self, url: str, city: str, start_page: int):
        while True:
            print(f'[Infinite Parser]: Started infinite parsing at {str(datetime.now())}')
            self.cars_links(url, city, start_page)
            print(f'[Infinite Parser]: Finished infinite parsing at {str(datetime.now())}')

    def cars_links(self, url: str, city: str, start_page: int):
        count_cars_in_db = 0
        page = start_page
        while True:
            if page != 1:
                r = self.make_request(conf.MAIN_URL + url + str(page))
            else:
                r = self.make_request(conf.MAIN_URL + '/cars/almaty/')
            soup = BeautifulSoup(r.text, 'lxml')
            divs_car = soup.select('div[class*="a-list__item"]')
            if not divs_car or (page != 1 and int(soup.find('h1').text.split(' ')[-1]) != page):
                break
            page += 1
            if count_cars_in_db >= 20:
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
                print("this is a car id: ",car_id)
                a = div.find('a', class_='a-card__link')
                adYellow = div.find('div', class_='a-card--pay-yellow')
                adBlue = div.find('div', class_='a-card--pay-yellow')
                if adYellow is not None:
                    advertisement = 'yellow'
                if adBlue is not None:
                    advertisement = 'blue'
                else: 
                    advertisement = 'null'
                date_of_publication = div.find('span', class_='a-card__param--date')
                if a is not None and date_of_publication is not None:
                    is_in_database = self.parse_car(car_id, advertisement, date_of_publication.text, a.get('href'))
                if is_in_database:
                    count_cars_in_db += 1
                else:
                    count_cars_in_db = 0
            print('page: ' + str(page))
            print("SELAM")
    

if __name__ == '__main__':
    print('Parsing Started!')
    p = InfiniteIdParser()
    city = sys.argv[1]
    print(city)
    url, city = conf.cities_dict[city]
    p.start_infinite_parsing(url, city, 1)