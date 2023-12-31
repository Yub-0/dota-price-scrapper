from fastapi import Request, FastAPI
from fastapi.middleware.cors import CORSMiddleware

import numpy as np
import pandas as pd
import datetime
import requests
import json
origins = ["*"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_data_dict(value):
    f = pd.DataFrame(value)
    new_df = f.loc[f['tradability'] == 'Tradable']
    new_df = new_df[['name', 'market_hash_name', 'classid', 'instanceid', 'assetid']]
    data_dict = {}
    for index, row in new_df.iterrows():
        if row["name"] not in data_dict:
            data_dict[row["market_hash_name"]] = {
                "price": None,
                "update_date": datetime.datetime.now().isoformat()
            }
    return data_dict

@app.post("/price")
async def get_body(request, item: Item):
    value = await request.json()

    file_path = 'C:/Users/yub/PycharmProjects/dotapricescrapper/itemprice.json'

    with open(file_path, 'r') as file:
        item_price_data = json.load(file)

    if not item_price_data:
        item_price_data = get_data_dict(value)
        with open(file_path, 'w') as file:
            json.dump(data_dict, file)

    for item in value:
        if item['name'] in item_price_data:
            if item_price_data[item['name']]['price']:
                date_now = datetime.datetime.fromisoformat(datetime.datetime.now().isoformat())
                up_date = datetime.datetime.fromisoformat(item_price_data[item['name']]['update_date'])
                time_dif = (date_now - up_date).total_seconds()
                if time_dif < 172800:
                    item['price']['price'] = item_price_data[item['name']]['price']
                    continue
        if item['tradability'] == 'Not Tradeable':
            continue
        url = 'https://steamcommunity.com/market/priceoverview/?country=NP&appid=570&market_hash_name=' + str(item['name'])
        try:
            market_price = requests.get(url)
            price = market_price.json()
            if price:
                price_value = price['lowest_price'].replace("$", "")  # Remove the currency symbol
                price_value = price_value.split(' ')[0]
                price_value = float(price_value)  # Convert to float
                item_price_data[item['name']]['price'] = item['price']['price'] = price_value
                item_price_data[item['name']]['update_date'] = datetime.datetime.now().isoformat()
        except Exception as e:
            print(e)
    with open(file_path, 'w') as file:
        json.dump(item_price_data, file)
    return value