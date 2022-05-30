#!/usr/bin/env python3
import boto3
import pymongo
from os.path import join
from bson import json_util
import gzip

# 5 settings to change 6 (variables)
AWS_ACCESS_KEY = 'AWS_ACCESS_KEY'
AWS_SECRET_KEY = 'AWS_SECRET_KEY'
urlAtlas = 'mongodb+srv://main_user:PASSWORD@CLUSTERID.mongodb.net/admin?retryWrites=true&w=majority'
bucket = 'S3_BUCKET_NAME'
unique_folder = 'firstname.lastname'

database = 'sample_mflix'
collection = 'theaters'

def connectS3():
    client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
    )
    return client


def connectMongoDB():
    print('Connect to Atlas Cluster...')
    client = pymongo.MongoClient(urlAtlas)
    return client


def offloadMongoDB(clientMongoDB, clientS3):
    print('Download data into file...')
    db = clientMongoDB[database]
    col = db[collection]

    # Here we can customize the query for partial offloading, e.g. data older than one day
    data = col.find()
    name = collection + ".json.gz"

    jsonpath = './' + name
    with gzip.GzipFile(jsonpath, 'wb') as fout:
        fout.write(json_util.dumps(data).encode('utf-8'))

    print('Upload data to S3 bucket...')
    clientS3.upload_file(
        Filename=jsonpath, Bucket=bucket, Key=unique_folder+'/'+collection+'/'+name)

if __name__ == '__main__':
    clientS3 = connectS3()
    clientMongoDB = connectMongoDB()
    offloadMongoDB(clientMongoDB, clientS3)
    print ('done')
