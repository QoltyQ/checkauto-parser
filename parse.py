import urllib3
import requests
import conf
from psql import Proxy
from bs4 import BeautifulSoup
from datetime import date, datetime
from db_utils import check_ip, save_connection, check_ready_ip, delete_used_ip
import json
import time
import sys
sys.stdout.flush()
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
        self.ip = None
        self.port = None

    def get_proxy(self, url, id, retries: int = 10) -> dict:
        while retries > 0:
            try:
                res = self.s.get('https://api.getproxylist.com/proxy?protocol[]=http&apiKey=20cdcf4236a1ba151a60ac1fab0b56fa550341a2&allowsHttps=1&all=1',
                                 timeout=5)
                x = res.json()['stats']['count']
                for i in range(int(x)):
                    used_ip, used_port = check_ready_ip(id)
                    r = res.json()[str(i)]
                    if used_ip and used_port:
                        ip = used_ip
                        port = used_port
                    else:
                        ip = r['ip']
                        port = r['port']
                        free_ip = check_ip(id, ip)
                        if free_ip == False:
                            continue
                    current_proxy = {
                        'http': f'http://{ip}:{port}',
                        'https': f'http://{ip}:{port}'
                    }
                    if self.proxy == None:
                        self.proxy = current_proxy
                        self.ip = ip
                        self.port = port
                    try:
                        response = self.s.get(
                            url, timeout=30, proxies=self.proxy, verify=False)
                        if (id == "nb_phones"):
                            response = self.s.get(
                                url, timeout=30, proxies=self.proxy, headers=conf.HEADERS, verify=False)
                        print(
                            f"[{str(datetime.now())}] Current connected proxy: ", self.ip, self.port, flush=True)
                        save_connection(id, ip, port)
                        return response
                    except requests.RequestException as e:
                        if self.ip == used_ip:
                            delete_used_ip(id)
                        print(
                            f'[{str(datetime.now())}] Got network error while trying to make request to kolesa.kz by ip {self.proxy}. Retrying {retries}. {e}', flush=True)
                        self.proxy = None
                        retries -= 1
                        if retries == 5:
                            retries = 10
            except Exception as e:
                print(
                    f'[{str(datetime.now())}] Got network error while trying to make request to getproxylist.com. Retrying {retries}. {e}', flush=True)
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
                                   '/', "nb_views")
                data = json.loads(r.text)
                views = data['data'][car_id]['nb_views']
                return views
            except Exception as e:
                time.sleep(2)
                retries -= 1
                if retries <= 1:
                    print(f'[{str(datetime.now())}] Cannot parse views of'.format(
                        car_id), e, flush=True)
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
        result = None
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
                    break
            if result != None:
                break
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
        return author

    def get_phone(self, car_id, referer):
        count_error = 0
        while True:
            headers = conf.HEADERS
            try:
                url = conf.APP_URL + conf.PHONE_URL + car_id + '/phones'
                r = self.s.get(url, headers=headers, timeout=20,
                               verify=False)
                phones = r.json()['phones']
                phones_str = ''
                for p in phones:
                    phones_str += p + ' | '
                phones_str = phones_str[:-3]
                return phones_str
            except:
                count_error += 1
                if count_error > 0:
                    return None
