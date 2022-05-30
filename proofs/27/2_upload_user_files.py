#!/usr/bin/env python3
from global_vars import *
from pymongo import MongoClient
import os, sys, getopt, time, gridfs, uuid, shutil, datetime

# Connection details
client = MongoClient(connStr)
db = client[dbName]
coll = db[collName]
fs = gridfs.GridFSBucket(db)

# Prompt user for script variables
userId = input("Remind me what the user id is again: ");
filePath = input("Local filesystem path of sample video file (or other media type) to upload to DB for this user (just press enter to use the default video provided with this proof): ");

if filePath == '':
    filePath = './myvideo.mp4'
 
# derive the filename
fileName = filePath[filePath.rfind("/")+1:]
print("Using file %s" % fileName);

# Get metadata for the file we fetched
meta = os.stat(fileName);
fileSize = meta.st_size;
print("File Size: %s" % fileSize);
fileExt = fileName[fileName.rfind(".")+1:]
print("File Extension: %s" % fileExt);
fileId = uuid.uuid4().hex;
print("File Id: %s" % fileId);
print("\nUploading file...")

# Upload file to gridfs 
with open(fileName, 'rb') as temp_file:
    fs.upload_from_stream_with_id(
        fileId,
        fileName,
        temp_file,
        chunk_size_bytes=160000, 
        metadata={"extension": fileExt})

# Add new upload file event log, referencing uploaded PDF
upload_file_event = {
    'date': datetime.datetime.now(),
    'fileExt': fileExt,
    'filePath': filePath,
    'fileName': fileName,
    'fileSize': fileSize,
    'fileId': fileId
}

coll.update_one({'user_id': userId}, {'$push': {'uploaded_files': upload_file_event}})

print('Successfully uploaded file for user: ' + userId)
