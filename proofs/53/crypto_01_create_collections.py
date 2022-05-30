import pymongo

import config

client = pymongo.MongoClient(config.CONNECTION_STRING)

client[config.DB_NAME].create_collection("cryptoRaw")
client[config.DB_NAME].create_collection("cryptoBuckets")

index_raw = pymongo.IndexModel([('timestamp', pymongo.ASCENDING)], name="timestamp")
index_buckets_timestamp = pymongo.IndexModel([('values.timestamp', pymongo.ASCENDING)], name="timestamp")
index_bucket_timestamp = pymongo.IndexModel([('bucketTimestamp', pymongo.DESCENDING)], name="bucketTimestamp")

client[config.DB_NAME].cryptoRaw.create_indexes([index_raw])
client[config.DB_NAME].cryptoBuckets.create_indexes([index_bucket_timestamp, index_buckets_timestamp])