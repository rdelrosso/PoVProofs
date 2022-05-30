#!/usr/bin/env python3

import pymongo
from bson.json_util import dumps
import time
import random
import demo_settings

def read_data(collection, doc_id):
    # dictionary to be added in the database
    item = collection.find({"emp_no" : doc_id})
    return item


if __name__ == "__main__":
    try:
        conn=pymongo.MongoClient(demo_settings.URI_STRING)

        print("Microservice Two - connected to MongoDB\n")

        db = conn["FLEXIBLE"]
        # username = db.command("connectionStatus")['authInfo']['authenticatedUsers'][0]['user']
        # collection = db[username]
        collection = db[demo_settings.COLLECTION_NAME]

        departments = collection.distinct("department")
        print("..departments..", departments)
        print()

        while True:
            print("Running employees report (microservice two)")
            dept = random.choice(departments)
            print("--ENQUIRY FOR DEPARTMENT: " + dept)
            items = collection.find({"department" : dept}, {"_id": 0, "gender": 0, "annual_salary":0, "hire_date": 0}).limit(5)
            for item in items:
                print(dumps(item))

            print("...\n")
            time.sleep(5)

        print("Operation completed successfully!!!")

    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDB: %s" % e)
    conn.close()
