#!/usr/bin/env python3
from global_vars import *
from pymongo import MongoClient
import sys, getopt, time, gridfs
from datetime import datetime

# Connection Details
client = MongoClient(connStr)
#   client.drop_database(dbName)
db = client[dbName]
coll = db[collName]

userId = input("Please provide a user id, e.g. abc123: ")
name = input("User's name: ");

user_record = {
    'user_id': userId,
    'name': name,
    'uploaded_files': []
}

print(user_record);

coll.insert_one(user_record)

print("Inserted user record");
