from datetime import datetime, tzinfo, timezone
import pandas
import pymongo
import time
import config

client = pymongo.MongoClient(config.CONNECTION_STRING)
buckets_collection = client[config.DB_NAME]['cryptoBuckets']

df = pandas.read_csv(config.FOLDERNAME + '/' + config.FILENAME)
df = df.iloc[::-1] # reverse data set, because it starts with the newest entries which is not a realistic use case

bulk_ops = []
counter = 0
start = time.time()

for row in df.itertuples():
    timestamp = datetime.strptime(row.date, '%Y-%m-%d %H:%M:%S')
    bucket_timestamp = timestamp.replace(minute=0, second=0)
    bulk_ops.append(pymongo.UpdateOne({ 
            "symbol": row.symbol,
            "bucketTimestamp": bucket_timestamp,
        },{ 
            "$push": { 
                "values": {
                    'timestamp': timestamp,
                    'open': row.open,
                    'high': row.high,
                    'low': row.low,
                    'close': row.close,
                    'VolumeBTC': row.VolumeBTC,
                    'VolumeUSDT': row.VolumeUSDT,
                    'tradecount': row.tradecount
                } },
            "$inc": { "count": 1 },
            "$min": { "minValue": row.low },
            "$max": { "maxValue": row.high },
            "$setOnInsert": { 
                "symbol": row.symbol,
                "bucketTimestamp": bucket_timestamp,
            }
        },
        upsert=True))

    if len(bulk_ops) > 1000:
        buckets_collection.bulk_write(bulk_ops)
        bulk_ops = []
        counter += 1000
        print(f'{counter} data points inserted')

end = time.time()
diff = end - start
rate = round(counter/diff)

print(f'Inserted with {rate} data points per second')