from bs4 import BeautifulSoup as bs
import html5lib
from datetime import datetime
import time
import requests
from random import choice

def proxy_generator():
    r = requests.get("https://sslproxies.org/")
    soup = bs(r.content, 'html5lib')

    proxy_list = soup.find_all('td')[::8]
    ports_list = soup.find_all('td')[1::8]

    combined_list = []
    i = 0

    while i < len(proxy_list):
        combined_list.append(f'{proxy_list[i].string}:{ports_list[i].string}')
        i+=1

    proxy = {'https': choice(combined_list)}

    return proxy

def scrape():

    # Can be changed to any category url
    url = 'https://www.roguefitness.com/weightlifting-bars-plates'

    while True:
        try:
            proxy = proxy_generator()
            print(f"Proxy: {proxy}")
            headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            r = requests.get(url, proxies=proxy, timeout=5, headers=headers)
            break
        except:
            print('Trying new proxy')
            pass

    page_content = bs(r.content, features='html5lib')
    all_product_names = page_content.select('h2.product-name')
    all_product_prices = page_content.select('span.price')

    names_prices = {}

    i = 0
    while i < len(all_product_names):
        product_name = (all_product_names[i]).find('a').string
        names_prices[f'{product_name}'] = (all_product_prices[i]).string
        i+=1

    return names_prices

scrape()