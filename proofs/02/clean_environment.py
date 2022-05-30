#!/usr/bin/env python3

import pymongo
import demo_settings
import certifi

if __name__ == "__main__":
    try:
        conn = pymongo.MongoClient(demo_settings.URI_STRING,tls=True, tlsCAFile=certifi.where())
        print("Connected to MongoDB")

        db = conn["FLEXIBLE"]
        # username = db.command("connectionStatus")['authInfo']['authenticatedUsers'][0]['user']
        # collection = db[username]
        collection = db[demo_settings.COLLECTION_NAME]

        print("Dropping Collection: FLEXIBLE."+demo_settings.COLLECTION_NAME)
        collection.drop()

        print("Operation completed successfully!!!")

    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDB: %s" % e)
    conn.close()
