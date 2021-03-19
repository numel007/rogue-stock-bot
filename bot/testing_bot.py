import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from bs4 import BeautifulSoup as bs
import html5lib
import requests
from random import choice
from models import Item, DeclarativeBase, db_connect, create_items_table
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
import json


load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='!')
engine = db_connect()
create_items_table(engine)
Session = sessionmaker(bind=engine)
db = Session()

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

def get_urls():
    with open(os.path.join(os.path.dirname(__file__), "products.json")) as file:
        data = json.load(file)

    bar_urls = []
    iron_plates_urls = []
    steel_plates_urls = []
    bumper_plates_urls = []
    all_urls = []

    # Parse bar urls
    for category, product_list in data["barbells"].items():
        for product, url in product_list.items():
            bar_urls.append(url)
    all_urls.append(bar_urls)

    # Parse iron plate urls
    for name, url in data["iron-plates"].items():
        iron_plates_urls.append(url)
    all_urls.append(iron_plates_urls)

    # Parse steel plate urls
    for lb_kg, url in data["steel-plates"].items():
        steel_plates_urls.append(url)
    all_urls.append(steel_plates_urls)

    # Parse bumper plate urls
    for category, brand in data["bumper-plates"].items():
        for version, products in brand.items():
            for name, url in products.items():
                bumper_plates_urls.append(url)
    all_urls.append(bumper_plates_urls)

    return all_urls

def scrape():
                
    animation = "|/-\\"
    idx = 0
    all_urls = get_urls()
    data_list = []

    while True:
        print(animation[idx % len(animation)], end="\r")
        idx += 1
        time.sleep(0.1)
        try:
            proxy = proxy_generator()
            headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            for i in range(len(all_urls)):
                for url in all_urls[i-1]:
                    r = requests.get(url, proxies=proxy, timeout=8, headers=headers)
                    print(f'Requesting {url}')
                    data_list.append(r)
            break
        except:
            pass

    print(data_list)
    results = {}
    for data_point in data_list:
        page_content = bs(data_point.content, features='html5lib')
        names = page_content.select('div.item-name')
        grouped_items = page_content.select('div.grouped-item-row')
        stock_status = []

        for item in grouped_items:
            if item.select('div.item-qty.input-text'):
                stock_status.append(1)
            else:
                stock_status.append(0)

        for i in range(len(names)):
            results[f'{names[i].string}'] = stock_status[i]

    print(results)
    return results

@bot.event
async def on_ready():
    print(f'{bot.user} is running.')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you."))

# Not working yet!
@bot.command()
async def bars(ctx):
    values = scrape()
    for name, price in values.items():
        await ctx.channel.send(f'{name}: {price}')
    await ctx.channel.send('------------------')

@bot.command()
async def check_plates(ctx):
    values = scrape()
    for name, stock_status in values.items():

        try:
            search_item = db.query(Item).filter_by(name=name).first()
            print(search_item.name)

            if search_item.stock_status != stock_status:
                search_item.stock_status = stock_status
                db.commit()
                print('Updating stock status')

            print('Duplicate found, skipping')

        except Exception as e:
            print(e)
            print('Adding to db')
            new_item = Item(
                name = name,
                stock_status = stock_status
            )
            db.add(new_item)
            db.commit()
    
bot.run(TOKEN)