MAIN_URL = 'https://kolesa.kz'
VIEWS_URL = '/ms/views/kolesa/live/'
PHONE_URL = '/a/ajaxPhones?id='
ASTANA_URL = '/cars/nur-sultan/?page='
ALMATY_URL = '/cars/almaty/?page='
SHYMKENT_URL = '/cars/shymkent/?page='

cities_dict = {
    'almaty': (ALMATY_URL, 'Алматы'),
    'astana': (ASTANA_URL, 'Нур-Султан (Астана)'),
    'shymkent': (SHYMKENT_URL, 'Шымкент')
}

HEADERS = {
    'authority': 'kolesa.kz',
    'scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}

keys_dict = {
    'Город': 'city',
    'Наличие': 'availability',
    'Кузов': 'car_body',
    'Объем двигателя, л': 'engine_volume',
    'Пробег': 'mileage',
    'Коробка передач': 'transmission',
    'Руль': 'steering_wheel',
    'Цвет': 'color',
    'Привод': 'drive',
    'Растаможен в Казахстане': 'customs_cleared',
}


def get_specifications_dict():
    d = dict()
    d['city'] = None
    d['availability'] = None
    d['car_body'] = None
    d['engine_volume'] = None
    d['mileage'] = None
    d['transmission'] = None
    d['steering_wheel'] = None
    d['color'] = None
    d['drive'] = None
    d['customs_cleared'] = None
    return d


def get_month(month_str: str) -> int:
    if 'ян' in month_str:
        return 1
    elif 'фе' in month_str:
        return 2
    elif 'мар' in month_str:
        return 3
    elif 'ап' in month_str:
        return 4
    elif 'мая' in month_str or 'май' in month_str:
        return 5
    elif 'июн' in month_str:
        return 6
    elif 'июл' in month_str:
        return 7
    elif 'ав' in month_str:
        return 8
    elif 'се' in month_str:
        return 9
    elif 'ок' in month_str:
        return 10
    elif 'но' in month_str:
        return 11
    elif 'дек' in month_str:
        return 12
