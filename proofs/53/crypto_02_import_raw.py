from datetime import datetime, tzinfo, timezone
import pandas
import pymongo
import time

import config

client = pymongo.MongoClient(config.CONNECTION_STRING)

raw_collection = client[config.DB_NAME]['cryptoRaw']

df = pandas.read_csv(config.FOLDERNAME + '/' + config.FILENAME)
df = df.iloc[::-1]

data_points = []
start = time.time()

counter = 0
for row in df.itertuples():
    data_points.append({
        'timestamp':datetime.strptime(row.date, '%Y-%m-%d %H:%M:%S'),
        'symbol':row.symbol,
        'open': row.open,
        'high': row.high,
        'low': row.low,
        'close': row.close,
        'VolumeBTC': row.VolumeBTC,
        'VolumeUSDT': row.VolumeUSDT,
        'tradecount': row.tradecount
    })

    if len(data_points) > 1000:
        raw_collection.insert_many(data_points)
        data_points = []
        counter += 1000
        print(f'{counter} data points inserted')

end = time.time()
diff = end - start
rate = round(counter/diff)

print(f'Inserted with {rate} data points per second')
