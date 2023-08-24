import numpy as np
import pandas as pd
import datetime
import requests
import json

from ninja import NinjaAPI
from ninja import Schema
from django.db import connection
api = NinjaAPI()


class RequestData(Schema):
    name: str


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

    # value_alt = value.replace(" ", "+")
    # url = 'https://steamcommunity.com/market/priceoverview/?country=NP&appid=570&market_hash_name=' + str(value)
    # url2 = (
    #     f"https://steamcommunity.com/market/search/render/?query={value_alt}&start=0&count=1&sort_column=popular&sort_dir=desc&"
    #     f"appid=570&norender=1")
    # try:
    #     market_price = requests.get(url)
    #     if market_price.status_code == 429:
    #         print('no response')
    #         raise
    #     price = market_price.json()
    #     if price and price['lowest_price']:
    #         price_value = price['lowest_price'].replace("$", "")  # Remove the currency symbol
    #         price_value = price_value.split(' ')[0]
    #         price_value = float(price_value)  # Convert to float
    #         item_price_data[value]['price'] = price_value
    #         item_price_data[value]['update_date'] = datetime.datetime.now().isoformat()
    # except Exception as e:
    #     try:
    #         market_price = requests.get(url2)
    #         if market_price.status_code == 429:
    #             raise
    #         data = market_price.json()
    #         if data and data['results']:
    #             desc = data['results'][0]
    #             price = desc['sale_price_text']
    #             price = price.replace("$", "")
    #             price_value = price.split(' ')[0]
    #             price_value = float(price_value)
    #             item_price_data[value]['price'] = price_value
    #             item_price_data[value]['update_date'] = datetime.datetime.now().isoformat()
    #     except:
    #         pass
    #
    with open(file_path, 'w') as file:
        json.dump(item_price_data, file, indent=4)
    print(item_price_data[value])
    return {value: item_price_data[value]}


@api.get("/price")
def get_body(request):
    with connection.cursor() as cursor:
        query = "SELECT * FROM price_item"
        df = pd.read_sql_query(query, connection)
        df.replace({np.nan: None}, inplace=True)
    json_data = df.set_index('name').to_dict(orient='index')
    return json_data

@api.get("/pricefromjson")
def get_price_json(request):
    file_path = 'C:/Users/yub/PycharmProjects/dotapricescrapper/itemprice.json'
    with open(file_path, 'r') as file:
        item_price_data = json.load(file)

    insert_data = []
    for product_name, product_info in item_price_data.items():
        price = product_info['price']
        update_date = product_info['update_date']
        insert_data.append((product_name, price, update_date))
    with connection.cursor() as cursor:
        query = "INSERT INTO price_item (name, price, update_date) VALUES (?, ?, ?)", insert_data
        cursor.executemany("INSERT INTO price_item (name, price, update_date) VALUES (?, ?, ?)", insert_data)

    return item_price_data