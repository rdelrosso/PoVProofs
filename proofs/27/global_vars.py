from pymongo import MongoClient
import os

connStr = "mongodb+srv://main_user:MyPassword@testcluster-abcde.mongodb.net/test?retryWrites=true"

dbName = "pov_multimedia"
collName = "users"
currDir = os.getcwd()  # get current directory
print('Current Directory: ' + currDir)
