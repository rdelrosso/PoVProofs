import time
import pymongo
import random

#Player Data (required to get a sample of 12 player ids)
client_A = pymongo.MongoClient("mongodb+srv://admin:********@playerCluster.l5iko.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db_A = client_A.sample_kafka
col_A = db_A.playerProfile

#Match Data (here the match data is stored after a match finished)
client_B = pymongo.MongoClient("mongodb+srv://admin:********@matchCluster.l5iko.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db_B = client_B.sample_kafka
col_B = db_B.matches

#Clear out old collection
db_B.drop_collection("matches")
#db_A.drop_collection("playerMatches")

insert_counter = 0
while True:
    sample_playerProfiles = col_A.aggregate([{ "$sample": { "size": 12 } }])
    match_array = []

    for playerProfile in sample_playerProfiles:
        new_match = {
            "playerId": playerProfile["playerId"],
            "geoLocale": f"{playerProfile['geo']}_{playerProfile['locale']}",
            "mvpWin": bool(random.getrandbits(1)),
            "totalMatchTimeSeconds": random.randint(0, 1500),
            "matchDataGained": {
                "gold": random.randint(0, 10000),
                "energy": random.randint(0, 10)
            },
            "matchCompleted": bool(random.getrandbits(1))
        }
        match_array.append(new_match)

    col_B.insert_many(match_array)
    print("Matches Batch #" + str(insert_counter) + " inserted!")
    insert_counter += 1
    time.sleep(5)
