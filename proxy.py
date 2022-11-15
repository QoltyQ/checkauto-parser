
import requests
s = requests.session()


def get_proxy(retries: int = 10) -> dict:
    while retries > 0:
        try:
            r = s.get('https://api.getproxylist.com/proxy?allowsCustomHeaders=1&allowsHttps=1&'
                      '%27%27%27%20%27allowsPost=1&apiKey=20cdcf4236a1ba151a60ac1fab0b56fa550341a2&%27%27country[]=AU&'
                      '%27%20%27maxConnectTime=1&minUptime=90&protocol[]=http',
                      timeout=5)
            print(r.json())
            current_proxy = {
                'http': f'http://{str(r.json().get("ip")) + ":" + str(r.json().get("port"))}',
                'https': f'http://{str(r.json().get("ip")) + ":" + str(r.json().get("port"))}'
            }
            print("Got new proxy: ", current_proxy, flush=True)
            r = s.get("https://jsonip.com/", timeout=10,
                      proxies=current_proxy, verify=False)
            print(r.json()['ip'])
            return r
        except:
            retries -= 1
            if retries == 1:
                retries = 2


proxs = {'https': 'http://157.100.12.139:999'}
s = requests.session()
r = s.get("https://jsonip.com/", proxies=proxs, verify=False)
print(r.json()['ip'])
