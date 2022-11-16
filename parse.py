import json
import time
from db_utils import car_to_db
from datetime import date, datetime
from bs4 import BeautifulSoup
import conf
import requests
import urllib3
urllib3.disable_warnings()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_date(date_str: str) -> date:
    day_month = date_str.split(' ')
    day = int(day_month[0])
    month = conf.get_month(day_month[1])
    year = 2022
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
        self.proxy = None

    def get_proxy(self, url, retries: int = 10) -> dict:
        while retries > 0:
            res = self.s.get('https://api.getproxylist.com/proxy?protocol[]=http&apiKey=20cdcf4236a1ba151a60ac1fab0b56fa550341a2&allowsHttps=1&all=1',
                             timeout=5)
            x = res.json()['stats']['count']
            for i in range(int(x)):
                r = res.json()[str(i)]
                ip = r['ip']
                port = r['port']
                current_proxy = {
                    'http': f'http://{ip}:{port}',
                    'https': f'http://{ip}:{port}'
                }
                if self.proxy == None:
                    self.proxy = current_proxy
                try:
                    response = self.s.get(
                        url, timeout=30, proxies=self.proxy, verify=False)
                    print("Current connected proxy: ", self.proxy, flush=True)
                    return response
                except requests.RequestException as e:
                    print(
                        f'Got network error while trying to make request to kolesa.kz by ip {self.proxy}. Retrying {retries}. {e}', flush=True)
                    self.proxy = None
                    retries -= 1
                    if retries == 5:
                        retries = 10

    def parse_brand_model(self, div) -> tuple:
        params = div.find_all('li')
        brand, model = params[-2].text.strip(), params[-1].text.strip()
        model = model.replace(brand, '').strip()
        return brand, model

    def parse_specifications(self, offer_parameters_div):
        spec_dict = conf.get_specifications_dict()
        try:
            spec_dict['condition'] = offer_parameters_div.find(
                'div', class_='offer__parameters-mortgaged').text.strip()
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
        while retries > 0:
            try:
                r = self.get_proxy(conf.MAIN_URL + conf.VIEWS_URL + car_id +
                                   '/', headers=headers, timeout=20, verify=False)
                data = json.loads(r.text)
                phones_views = data['data'][car_id]['nb_phone_views']
                views = data['data'][car_id]['nb_views']
                return views, phones_views
            except Exception as e:
                time.sleep(2)
                retries -= 1
                if retries <= 1:
                    print('Cannot parse views of {}. {}'.format(
                        car_id, e), flush=True)
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

    def parse_generation(self, generation_div):
        result = ''
        if not generation_div:
            return None
        generation = ''
        count = 0
        for div in generation_div:
            generation = div.find('dd', class_='value')
            for value in generation:
                count += 1
                if count == 2:
                    result = value
        return result

    def parse_likes(self, likes_div):
        likes = ''
        views = ''
        if not likes_div:
            return None
        count = 0
        for div in likes_div:
            count += 1
            if count == 4:
                likes = div
            if count == 2:
                views = div
        return likes, views

    def get_author(self, soup):
        author = 'Хозяин'
        if soup.find('div', class_='shop__info-container'):
            author = soup.find(
                'div', class_='shop__info-container').find('a').text.strip()
        else:
            author_text = soup.find(
                'h6', class_='offer__subtitle').text.strip()
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
                r = self.get_proxy(url, headers=headers, timeout=20, proxies=self.current_proxy,
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
