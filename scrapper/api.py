from ninja import NinjaAPI
import numpy as np
import pandas as pd
import datetime
import requests
import json
from typing import List, Any
from ninja import Schema

api = NinjaAPI()


@api.post("/price")
async def get_body(request, request_data: RequestData):
    value = request_data.name
    file_path = 'C:/Users/yub/PycharmProjects/dotapricescrapper/itemprice.json'

    with open(file_path, 'r') as file:
        item_price_data = json.load(file)

    if value not in item_price_data:
        item_price_data[value] = {
            "price": 0,
            "update_date": datetime.datetime.now().isoformat()
        }
    value_alt = value.replace(" ", "+")
    url = 'https://steamcommunity.com/market/priceoverview/?country=NP&appid=570&market_hash_name=' + str(value)
    url2 = (
        f"https://steamcommunity.com/market/search/render/?query={value_alt}&start=0&count=1&sort_column=popular&sort_dir=desc&"
        f"appid=570&norender=1")
    try:
        market_price = requests.get(url)
        if market_price.status_code == 429:
            print('no response')
            raise
        price = market_price.json()
        if price and price['lowest_price']:
            price_value = price['lowest_price'].replace("$", "")  # Remove the currency symbol
            price_value = price_value.split(' ')[0]
            price_value = float(price_value)  # Convert to float
            item_price_data[value]['price'] = price_value
            item_price_data[value]['update_date'] = datetime.datetime.now().isoformat()
    except Exception as e:
        try:
            market_price = requests.get(url2)
            if market_price.status_code == 429:
                raise
            data = market_price.json()
            if data and data['results']:
                desc = data['results'][0]
                price = desc['sale_price_text']
                price = price.replace("$", "")
                price_value = price.split(' ')[0]
                price_value = float(price_value)
                item_price_data[value]['price'] = price_value
                item_price_data[value]['update_date'] = datetime.datetime.now().isoformat()
        except:
            pass

    with open(file_path, 'w') as file:
        json.dump(item_price_data, file)
    print(item_price_data[value])
    return {value: item_price_data[value]}


@api.get("/price")
async def get_body(request):
    file_path = 'C:/Users/yub/PycharmProjects/dotapricescrapper/itemprice.json'
    with open(file_path, 'r') as file:
        item_price_data = json.load(file)
    return item_price_data
