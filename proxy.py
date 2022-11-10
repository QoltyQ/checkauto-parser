import requests
import urllib3
urllib3.disable_warnings()
import conf
from bs4 import BeautifulSoup
from datetime import date, datetime
from db_utils import car_to_db
import time
import json

def get_params(object):
        params = ''
        for key,value in object.items():
            if list(object).index(key) < len(object) - 1:
                params += f"{key}={value}."
            else:
                params += f"{key}={value}"
        return params
    
API_KEY = '5DPWr13oS1NI0EutAhym2tHvpuvYzlvF'

TARGET_URL = 'https://jsonip.com/'

PARAMETERS = {
    "proxy_type":"datacenter",
    "device":"desktop",
    "session":1
}


PROXY = {
    "http": f"http://webscrapingapi.{ get_params(PARAMETERS) }:{ API_KEY }@proxy.webscrapingapi.com:80",
    "https": f"https://webscrapingapi.{ get_params(PARAMETERS) }:{ API_KEY }@proxy.webscrapingapi.com:8000"
}
count = 0

lastProxy = PROXY

while True:
    count+=1
    print(lastProxy)
    response = requests.get(
        url=TARGET_URL,
        proxies=lastProxy,
        verify=False
    )
    if count == 3:
        lastProxy = PROXY
        count = 0

    print(response.text)