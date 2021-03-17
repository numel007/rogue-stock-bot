from bs4 import BeautifulSoup as bs
import html5lib
from datetime import datetime
import time
import requests
from random import choice

def proxy_generator():
    response = requests.get("https://sslproxies.org/")
    soup = bs(response.content, 'html5lib')

    proxy_list = soup.find_all('td')[::8]
    ports_list = soup.find_all('td')[1::8]

    combined_list = []
    i = 0

    while i < len(proxy_list):
        combined_list.append(f'{proxy_list[i].string}:{ports_list[i].string}')
        i+=1

    proxy = {'https': choice(combined_list)}

    return proxy

def scrape_bumpers():
    url = 'https://www.roguefitness.com/weightlifting-bars-plates/bumpers/competition-bumpers'

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
    all_products = page_content.select('h2.product-name')

    names = []

    for product in all_products:
        product_name = product.find('a').string
        names.append(product_name)

    print(names)


scrape_bumpers()