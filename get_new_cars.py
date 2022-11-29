from parse import Parser, get_date
from db_utils import create_new_car, save_connection
from datetime import datetime
from bs4 import BeautifulSoup
import conf
import urllib3
from random import randint
import time
import sys
sys.stdout.flush()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class InfiniteParser(Parser):
    def start_infinite_parsing(self, url: str, city: str, start_page: int):
        while True:
            print(
                f'[Infinite Parser]: Started infinite parsing at {str(datetime.now())}', flush=True)
            self.mobile_site_infinite(url, city, start_page)
            print(
                f'[Infinite Parser]: Finished infinite parsing at {str(datetime.now())}', flush=True)
            time.sleep(randint(120, 180))

    def mobile_site_infinite(self, url: str, city: str, start_page: int):
        count_cars_in_db = 0
        page = start_page
        while True:
            if page != 1:
                if page <= 1000:
                    r = self.get_proxy(conf.MOBILE_URL +
                                       url + str(page), "get_new_cars")
                else:
                    break
            else:
                r = self.get_proxy(conf.MOBILE_URL +
                                   '/cars/almaty/', "get_new_cars")
            soup = BeautifulSoup(r.text, 'lxml')
            divs_car = soup.select('div[class*="search-list__item"]')
            if not divs_car or (page != 1 and int(soup.find('h1').text.split(' ')[-1]) != page):
                break
            print(f'[{str(datetime.now())}] page: ' + str(page), flush=True)
            page += 1
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
                advertisement = 'yellow' if adYellow is not None else 'blue' if adBlue is not None else 0
                city = div.find(
                    'div', class_="a-card-info__region").text.strip()
                price = div.find(
                    'div', class_="a-card-price").text.strip()
                description = div.find_all(
                    'span', class_="a-card-info__description-item")
                year = description[0].text.strip()
                year = year[0:4]
                footer = div.find('div', class_="a-card-footer")
                likes, views = self.parse_likes(footer.find_all('span'))
                temp = likes and likes.text.strip() or 0
                # tempv = views and views.text.strip() or 0
                date_of_publication = footer.find('div').text.strip()
                date = get_date(date_of_publication)

                if a is not None and date_of_publication is not None:
                    is_new_car_created = create_new_car(
                        car_id, city, None, None, price, year, advertisement, temp, None, date)
                if not is_new_car_created:
                    print(f"[{str(datetime.now())}] {car_id} already in db")
                    count_cars_in_db += 1
                else:
                    print(f"[{str(datetime.now())}] {car_id} added")
                    count_cars_in_db = 0
            if count_cars_in_db >= 150:
                break
            start_page = page
            time.sleep(randint(30, 90))


if __name__ == '__main__':
    print(f'[{str(datetime.now())}] Parsing Started!', flush=True)
    p = InfiniteParser()
    city = 'almaty'
    url, name = conf.cities_dict[city]
    p.start_infinite_parsing(url, name, 1)
