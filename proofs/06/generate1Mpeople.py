#!/usr/bin/env python3
# call with parameter: MongoDB URI.

import random
import sys
import time
from multiprocessing import Process
from faker import Factory
from pymongo import MongoClient, WriteConcern
from pymongo.errors import BulkWriteError, PyMongoError
from pymongo import InsertOne
import certifi

# for country codes
ccFile = "countryCodes.txt"

# Number of processes to launch
processesNumber = 8 #DO NOT CHANGE as it must match updateAndCheck code
processesList = []

# batch size and bulk size per process
batchSize = 125000 #DO NOT CHANGE as it must match updateAndCheck code
bulkSize = 1000

# Settings for Faker, change locale to create other language data
fake = Factory.create('fr_FR')  # fr_FR is almost 10 times faster than en_US


# loads all country codes from file
def read_country_codes():
    with open(ccFile) as f:
        codes = f.read().splitlines()
    print("read", str(len(codes)), "country codes from file", ccFile)
    return codes


# Main processes code
def run(process_id, uri, codes):
    country_codes_count = len(codes)

    print("process", process_id, "connecting to MongoDB...")
    connection = MongoClient(host=uri, socketTimeoutMS=10000, connectTimeoutMS=10000, serverSelectionTimeoutMS=10000,tlsCAFile=certifi.where())
    people_collection = connection.world.get_collection("people", write_concern=WriteConcern(w="majority", wtimeout=8000))
    
    bulkRequest = []
    for j in range(batchSize):
        bulkRequest.append(InsertOne({
            "process": process_id,
            "index": j,
            "lastName": fake.last_name(),
            "firstName": fake.first_name(),
            "ssn": fake.ssn(),
            "job": fake.job(),
            "phone": [
                {"type": "home", "number": fake.phone_number()},
                {"type": "cell", "number": fake.phone_number()}
            ],
            "address": {
                "street": fake.street_address(),
                "city": fake.city()
            },
            "revenue": random.randint(50000, 250000),
            "age": random.randint(20, 60),
            "location": codes[random.randint(1, country_codes_count - 1)]
        }))

        if (j + 1) % bulkSize == 0:
            try:
                people_collection.bulk_write(bulkRequest,ordered=False)
                print('%s - process %s - records %s' % (time.strftime("%H:%M:%S"), process_id, j + 1))
        
                bulkRequest = []
            except BulkWriteError as bwe:
                print(bwe.details)
                print("Process {process_id} died - fix the issue as not all data will have loaded")
                sys.exit(1)
            except PyMongoError as e:
                print("failed to write to MongoDB cluster with URI", uri, "with error", e)
                print("Process {process_id} died - fix the issue as not all data will have loaded")
                sys.exit(2)


# Main
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("You forgot the MongoDB URI parameter!")
        print(" - example: mongodb://mongo1,mongo2,mongo3/test?replicaSet=replicaTest&retryWrites=true")
        print(" - example: mongodb+srv://user:password@cluster0-abcde.mongodb.net/test?retryWrites=true")
        exit(1)
    mongodb_uri = str(sys.argv[1])

    country_codes = read_country_codes()

    print("launching", str(processesNumber), "processes...")

    # Creation of processesNumber processes
    for i in range(processesNumber):
        process = Process(target=run, args=(i, mongodb_uri, country_codes))
        processesList.append(process)

    # launch processes
    for process in processesList:
        process.start()

    # wait for processes to complete
    for process in processesList:
        process.join()
