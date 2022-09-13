import conf
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
        page = start_page
        while True:
            r = self.make_request(conf.MAIN_URL + url + str(page))
            soup = BeautifulSoup(r.text, 'lxml')
            divs_car = soup.select('div[class*="row vw-item list-item"]')
            if not divs_car or (page != 1 and int(soup.find('h1').text.split(' ')[-1]) != page):
                break
            for div in divs_car:
                if div is None:
                    break
                car_id = div.get('data-id')

                advertisement = get_advertisement(div.attrs['class'])
                is_changed = change_date_of_editing_in_db(car_id)
                if is_changed:
                    print(f'date of apartment: {car_id} is changed')
                else:
                    print(f'apartment {car_id} is not in db')
                    a = div.find('a', class_='list-link ddl_product_link')
                    date_of_publication = div.find('span', class_='date').text.strip()
                    self.parse_car(car_id, advertisement, date_of_publication, a.get('href'))
            print('page: ' + str(page))
            page += 1


if __name__ == '__main__':
    print('Parsing Started!')
    p = InfiniteIdParser()
    city = sys.argv[1]
    url, city = conf.cities_dict[city]
    p.start_infinite_parsing(url, city, 1)