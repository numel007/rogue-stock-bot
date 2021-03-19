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

def scrape():
    url = 'https://www.roguefitness.com/rogue-calibrated-lb-steel-plates'

    animation = "|/-\\"
    idx = 0
    while True:
        print(animation[idx % len(animation)], end="\r")
        idx += 1
        time.sleep(0.1)
        try:
            proxy = proxy_generator()
            headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            r = requests.get(url, proxies=proxy, timeout=1.5, headers=headers)
            break
        except:
            pass

    print('Found working proxy\n')
    page_content = bs(r.content, features='html5lib')
    names = page_content.select('div.item-name')
    grouped_items = page_content.select('div.grouped-item-row')
    stock_status = []

    for item in grouped_items:
        if item.select('div.item-qty.input-text'):
            stock_status.append(1)
        else:
            stock_status.append(0)

    results = {names[i].string: stock_status[i] for i in range(len(names))}
    return results

@bot.command()
async def ping(ctx):
    print('Command recieved: !ping')
    print(ctx.author)
    await ctx.channel.send('pong')

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
        print(name, stock_status)

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