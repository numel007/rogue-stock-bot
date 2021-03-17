import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from bs4 import BeautifulSoup as bs
import html5lib
from datetime import datetime
import time
import requests
from random import choice


load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='!')

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

def scrape(category):

    # Can be changed to any category url
    url = 'https://www.roguefitness.com/weightlifting-bars-plates?cat2%5B0%5D=barbells_id_4669'

    while True:
        try:
            proxy = proxy_generator()
            print(f"Proxy: {proxy}")
            headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            r = requests.get(url, proxies=proxy, timeout=3, headers=headers)
            break
        except:
            print('Trying new proxy')
            pass

    print('Found working proxy')
    page_content = bs(r.content, features='html5lib')
    all_product_names = page_content.select('h2.product-name')
    all_product_prices = page_content.select('span.price')

    names_prices = {}

    i = 0
    while i < len(all_product_names):
        product_name = all_product_names[i].find('a').string
        names_prices[f'{product_name}'] = float((all_product_prices[i]).string.replace('$', ''))
        i+=1

    return names_prices


def check_olympic_plates():
    url = 'https://www.roguefitness.com/rogue-calibrated-lb-steel-plates'
    while True:
        try:
            proxy = proxy_generator()
            print(f"Proxy: {proxy}")
            headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            r = requests.get(url, proxies=proxy, timeout=3, headers=headers)
            break
        except:
            print('Trying new proxy')
            pass

    print('Found working proxy')
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

@bot.command()
async def bars(ctx):
    values = scrape('bars')
    for name, price in values.items():
        await ctx.channel.send(f'{name}: {price}')
    await ctx.channel.send('------------------')

@bot.command()
async def check_plates(ctx):
    values = check_olympic_plates()
    for name, stock_status in values.items():
        if stock_status == 1:
            await ctx.channel.send(f'{name}: In stock!')
        else:
            await ctx.channel.send(f'{name}: OOS!')
    
bot.run(TOKEN)