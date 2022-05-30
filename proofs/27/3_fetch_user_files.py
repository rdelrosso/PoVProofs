#!/usr/bin/env python3
from global_vars import *
from pymongo import MongoClient
import os, sys, getopt, time, gridfs, urllib.request, uuid, shutil, datetime

# Connection details
client = MongoClient(connStr)
db = client[dbName]
coll = db[collName]
fs = gridfs.GridFSBucket(db)

# Prompt user for script variables
userId = input("Remind me what the user id is again: ");

# Find user record
result = coll.find_one({'user_id' : userId})
fileId = None

# Make a downloads directory
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# Loop thru upload file event sub-docs looking for fileId
for uploadEvent in result['uploaded_files']:
    fileId = uploadEvent['fileId']

    # Retrieve referenced file content
    files = fs.find({'_id': fileId})

    for file in files:
        with open("downloads/" + file.filename, 'wb') as outfile:
            outfile.write(file.read())
            print("Downloading %s locally" % file.filename)

