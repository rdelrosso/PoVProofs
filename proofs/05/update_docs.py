#!/usr/bin/env python3

import pymongo
import random
from pymongo import UpdateOne
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
	
	# Loop through updates indefinitely
	while (True):
		docs = []
		i = int(1)

		# Skip cursor to a random place in the collection
		for c in col.find(skip=random.randint(0,999000)):

			# Cycle through a random # of documents between randint(<range>)
			if i <= random.randint(999,1111):
				# Assign random new value
				new_region = random.randint(2000,9999)

				# Append the update to the docs array
				docs.append(UpdateOne({'_id': c['_id']}, {'$set': {'region': new_region}}))
				i = i+1
			else:
				# Once enough documents have been added to docs array, bulk_write them to Atlas
				result = col.bulk_write(docs, ordered=False)
				print("number of records updated: "+str(result.modified_count))
				break

####
# Main
####
if __name__ == '__main__':
	main()
