#!/usr/bin/env python3

import pymongo
import random
import sys
import datetime

def main():
	if len(sys.argv) < 2:
		print('Error: No URL argument provided')
		sys.exit(-1)

	url = sys.argv[1].strip()

	# Connect to Atlas
	client = pymongo.MongoClient(url, readPreference="secondaryPreferred", readPreferenceTags="nodeType:ANALYTICS")
	db = client["acme_inc"]
	col = db["customers"]

	start = start = datetime.datetime(2017, 1, 1)
	end = datetime.datetime(2018, 1, 1, 23, 59, 59)

	policy_types = ['auto', 'home', 'life']
	states = ["AK","AL","AR","AZ","CA","CO","CT","DC","DE","FL","GA","HI","IA","ID","IL","IN","KS","KY","LA",
              "MA","MD","ME","MI","MN","MO","MS","MT","NC","ND","NE","NH","NJ","NM","NV","NY","OH","OK","OR",
              "PA","RI", "SC","SD","TN","TX","UT","VA","VT","WA","WI","WV","WY"]
	
	# Loop through queries indefinitely
	while (True):
		random_int = random.randint(0,999)
		policy = policy_types[random_int%3]
		state = states[random_int%50]
		pipeline = [
            {'$match': {
                'policies.nextRenewalDt': {'$gte': start,'$lte': end},'policies.policyType': policy,'policies.address.state': state
            }},
            {'$bucket': {
                'groupBy': "$region", 
                  'boundaries': [ 0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800],
                  'default': "Other",
                  'output': {"count": {'$sum': 1 }
                }
            }}
        ]
		print(f"\nPolicy: {policy}, State: {state}")
		i = int(1)
		for doc in col.aggregate(pipeline):
			print(f" - {doc}")

####
# Main
####
if __name__ == '__main__':
	main()
