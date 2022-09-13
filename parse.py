import requests
import urllib3
import conf
from bs4 import BeautifulSoup
from datetime import date, datetime
from db_utils import car_to_db
import time
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_date(date_str: str) -> date:
    day_month = date_str.split(' ')
    day = int(day_month[0])
    month = conf.get_month(day_month[1])
    year = 2020
    return date(year, month, day)


def get_advertisement(classes):
    if 'blue' in classes:
        return 'blue'
    if 'yellow' in classes:
        return 'yellow'
    return None


class Parser:
    def __init__(self):
        self.s = requests.session()
        self.current_proxy = None

    def get_proxy(self, retries: int = 10) -> dict:
        while retries > 0:
            try:
                r = self.s.get('https://api.getproxylist.com/proxy?allowsCustomHeaders=1&allowsHttps=1&'
                               '%27%27%27%20%27allowsPost=1&apiKey=20cdcf4236a1ba151a60ac1fab0b56fa550341a2&%27%27country[]=UA&'
                               '%27%20%27maxConnectTime=1&minUptime=90&protocol[]=http',
                               timeout=5)
                current_proxy = {
                    'http': f'http://{str(r.json().get("ip")) + ":" + str(r.json().get("port"))}',
                    # 'https': f'https://{str(r.json().get("ip")) + ":" + str(r.json().get("port"))}'
                }
                print(current_proxy)
                self.current_proxy = current_proxy
                return current_proxy
            except:
                retries -= 1
                if retries == 1:
                    retries = 2

    def make_request(self, url, retries: int = 10):
        while retries > 0:
            try:
                r = self.s.get(url, timeout=10, proxies=self.get_proxy(), verify=False)
                return r
            except requests.RequestException as e:
                print(f'{e}')
                retries -= 1
                if retries == 2:
                    retries = 3
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
                a = div.find('a', class_='list-link ddl_product_link')

                advertisement = get_advertisement(div.attrs['class'])
                date_of_publication = div.find('span', class_='date').text.strip()
                self.parse_car(car_id, advertisement, date_of_publication, a.get('href'))
            page += 1
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
                car_to_db(car_id, spec_dict['city'], advertisement, brand, model, year, spec_dict['condition'],
                          spec_dict['availability'], spec_dict['car_body'],
                          spec_dict['engine_volume'], spec_dict['mileage'], spec_dict['transmission'],
                          spec_dict['steering_wheel'], spec_dict['color'], spec_dict['drive'],
                          spec_dict['customs_cleared'], author, phone, views, phone_views, description, price,
                          date_of_publication_db, status)
                print(f'{car_id} added to db')
                return
            except:
                count_error += 1
                if count_error > 9:
                    return

    def parse_brand_model(self, div) -> tuple:
        params = div.find_all('li')
        brand, model = params[-2].text.strip(), params[-1].text.strip()
        model = model.replace(brand, '').strip()
        return brand, model

    def parse_specifications(self, offer_parameters_div):
        spec_dict = conf.get_specifications_dict()
        try:
            spec_dict['condition'] = offer_parameters_div.find('div', class_='offer__parameters-mortgaged').text.strip()
        except:
            spec_dict['condition'] = 'На ходу'
        dl_s = offer_parameters_div.find_all('dl')
        if len(dl_s) > 0:
            for dl in dl_s:
                column = dl.find('dt').text.strip()
                try:
                    key = conf.keys_dict[column]
                except:
                    continue
                value = dl.find('dd').text.strip()
                spec_dict[key] = value
        if spec_dict['availability'] is None:
            spec_dict['availability'] = 'В наличии'
        return spec_dict

    def parse_views(self, car_id: str, retries: int = 10) -> tuple:
        headers = conf.HEADERS
        headers['referer'] = conf.MAIN_URL + '/a/show/' + car_id
        headers['path'] = conf.VIEWS_URL + car_id + '/'
        while retries > 0:
            try:
                r = self.s.get(conf.MAIN_URL + conf.VIEWS_URL + car_id + '/', headers=headers, timeout=20,
                               proxies=self.get_proxy(), verify=False)
                data = json.loads(r.text)
                views = int(data['data'][car_id]['nb_views'])
                phone_views = int(data['data'][car_id]['nb_phone_views'])
                return views, phone_views
            except Exception as e:
                time.sleep(2)
                retries -= 1
                if retries <= 1:
                    print('Cannot parse views of {}. {}'.format(car_id, e))
                    return None, None

    def parse_description(self, description_div):
        if not description_div:
            return None
        description = ''
        divs = description_div.find_all('div', class_='text')
        for div in divs:
            for p in div.find_all('p'):
                description += p.text.strip()
                description += '\n'
        return description

    def get_author(self, soup):
        author = 'Хозяин'
        if soup.find('div', class_='shop__info-container'):
            author = soup.find('div', class_='shop__info-container').find('a').text.strip()
        else:
            author_text = soup.find('h6', class_='offer__subtitle').text.strip()
            if author_text != 'Контакты продавца':
                author = author_text.replace('Контакты ', '')
        return author

    def get_phone(self, car_id, referer):
        count_error = 0
        while True:
            headers = conf.HEADERS
            headers['referer'] = conf.MAIN_URL + referer
            try:
                url = conf.MAIN_URL + conf.PHONE_URL + car_id
                r = self.s.get(url, headers=headers, timeout=20, proxies=self.current_proxy,
                               verify=False)
                phones = r.json()['phones']
                phones_str = ''
                for p in phones:
                    phones_str += p + ' | '
                phones_str = phones_str[:-3]
                return phones_str
            except:
                count_error += 1
                if count_error > 9:
                    return None

if __name__ == '__main__':
    print('Parsing Started!')
    p = Parser()
    p.parse_car('135801340', None, '14 сентября', '/a/show/135801340')