#!/usr/bin/env python3

import os, sys, getopt, getpass, argparse
import srvlookup      #pip install srvlookup
import dns.resolver   #pip install dnspython
import time, random, hashlib
from pymongo import MongoClient

####
# READ_DATA is main routine. Reads from a changestream all changes
# that write_data is adding. Each string of data is added to hashlib
# and std output is updated with the moving MD5 hash
####
def read_data(proof12):
    # setup a md5 checksum
    h = hashlib.md5()

    seq = 1
    cursor = proof12.watch()
    try:
       for doc in cursor:
            try:
               # hashlib.update works cummullative.
               # Repeated calls are equivalent to a single call with
               # the concatenation of all the arguments
               h.update(doc['fullDocument']['random'].encode())
               print("Seq: ", seq," md5:",h.hexdigest())
               sys.stdout.flush()
               seq += 1
            except:
               print("Cannot read: No cluster instance available for reading?")
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
    client = MongoClient(con,username=user, password=pwd)
    db = client["PoV"]

    # Drop proof12 collection to make sure it is empty
    db.proof12.drop()

    # Now make sure it exist and empty
    proof12 = db.create_collection('proof12')

    return proof12

####
# Setup command line parameter so users can supply connection URI and
# optional username and password in a safe way.
####
def process_args():
    p = argparse.ArgumentParser()
    p.add_argument('-c','--connection',
                         help='URI connection', required=True)
    p.add_argument('-u','--username',
                         help='Username if not in connection string', required=False)
    p.add_argument('-p','--password',
                         help='Password if not in connection string', required=False)
    args = p.parse_args()
    if (args.username and (args.password is None)) :
        pwd=getpass.getpass(prompt='Password: ', stream=None)
        args.password = pwd
    if ((args.username is None) != (args.password is None)) :
        print("Must supply both username and password")
        exit()
    return(args)

if __name__ == "__main__":
   args = process_args()
   col = prereqs(args.connection,args.username,args.password)
   read_data(col)

