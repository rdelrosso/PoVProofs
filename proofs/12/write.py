#!/usr/bin/env python3

import os, sys, getopt, getpass, argparse
import srvlookup      #pip3 install srvlookup
import dns.resolver   #pip3 install dnspython
import time, random, hashlib
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid

####
# WRITE_DATA is main routine. At writeSpeed a random string of data
# is inserted in MongoDB. Each strings is added to hashlib and
# std output is updated with the moving MD5 hash
####
def write_data(proof12, speed):
    # setup a md5 checksum
    h = hashlib.md5()

    seq = 1
    try:
        while True:
            try:
               # Create random data to be added to MongoDB cluster
               rvalue = random.getrandbits(128)

               # Insert data as hex string value for readability
               proof12.insert_one({ "random" : hex(rvalue) })

               # Now we successfully have written document to cluster
               # update the hash and the sequences number
               h.update(hex(rvalue).encode())
               print("Seq: ", seq," md5:",h.hexdigest())
               sys.stdout.flush()
               seq += 1
            except:
               print("Cannot write: No primary available for writes?")
               print("make sure you use retryWrites=true to prevent this error")
            time.sleep(1/(speed))
    except KeyboardInterrupt:
        keyboard_shutdown()

####
# Swallow the verbiage that is spat out when using 'Ctrl-C' to kill the script
# and instead just print a simple single line message
####
def keyboard_shutdown():
    print('\Interrupted\n')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
####
# Check all prerequesites - mainly read.py must be started
# before write.py
####
def prereqs(con,user,pwd) :
    client = MongoClient(con,username=user,password=pwd,retryWrites=True)
    db = client["PoV"]

    # Collection must exist and must be empty
    try:
        # will create the collection, which should fail
        proof12 = db.create_collection('proof12')
        print("Start read.py before write.py!")
        # because collections is created, drop it!
        proof12.drop()
        sys.exit(0)
    except CollectionInvalid:
        # Collection exists, but is it empty?
        proof12 = db['proof12']
        
    # Now we are good. Collection exists and is empty
    # And this script did not create it, must be by read.py
    return proof12

####
# Setup command line parameter so users can supply connection URI and
# optional username and password in a safe way.
####
def process_args():
    p = argparse.ArgumentParser()
    p.add_argument('-c','--connection',
                         help='MongoDB URI connection', required=True)
    p.add_argument('-u','--username',
                         help='Username if not in connection string', required=False)
    p.add_argument('-p','--password',
                         help='Password if not in connection string', required=False)
    p.add_argument('-s','--writeSpeed',
                         help='# of records/s (default=2)', required=False)

    args = p.parse_args()
    if (args.writeSpeed) :
        args.writeSpeed = int(args.writeSpeed)
    else :
        args.writeSpeed = 2
    if (args.username and (args.password is None)) :
        pwd=getpass.getpass(prompt='Password: ', stream=None)
        args.password=pwd
    if ((args.username is None) != (args.password is None)) :
        print("Must supply both username and password")
        exit()
    return(args)

if __name__ == "__main__":
   args = process_args()
   col = prereqs(args.connection,args.username,args.password)
   write_data(col,args.writeSpeed)

