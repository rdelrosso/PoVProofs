#!/usr/bin/env python3
# call with parameter: MongoDB URI.

import random
import sys
import time
from multiprocessing import Process, Queue
from pymongo import MongoClient, WriteConcern

debug = True  # if true, will log successful consistent reads. if false, only logs missed reads

# file to log trace
logFileName = "consistency.log"

# Number of processes to launch - DO NOT CHANGE
processesNumber = 8 #DO NOT CHANGE as it must match generate code
processesList = []
# Number of iterations per process, and modulo for progress report
loops = 1000000
loopsPrint = 10


# Queue to write in the log file
def log_queue(my_queue, stop_token, logfile):
    with open(logfile, 'w') as f:
        while True:
            line = my_queue.get()
            if line == stop_token:
                f.close()
                return
            f.write(line)

def update_people(people, session, process_id, index_find, age_write, log):
    try:
        result = people.update_one({'process': process_id, 'index': index_find}, {'$set': {'age': age_write}},
                          session=session)
        return result.matched_count == 1
    except Exception as e:
        log.put("WRITE ERROR - " + time.strftime("%H:%M:%S") + " - process " + str(process_id) + " - index " + str(
            index_find) + " - age " + str(age_write) + "\n")
        print(e)
        return False

def find_people(people, session, process_id, index_find, log):
    try:
        return people.find_one({'process': process_id, 'index': index_find},
                               {'_id': 0, 'process': 1, 'index': 1, 'age': 1},
                               session=session)
    except Exception as e:
        log.put("READ ERROR - " + time.strftime("%H:%M:%S") + " - process " + str(process_id) + " - index " + str(
            index_find) + "\n")
        print(e)

def run(process_id, uri, log):
    print("process", process_id, "connecting to MongoDB...")
    connection = MongoClient(host=uri, w="majority", readPreference="secondaryPreferred", readConcernLevel="majority",
                             socketTimeoutMS=2000, connectTimeoutMS=2000, serverSelectionTimeoutMS=2000)

    people_collection = connection.world.get_collection("people",
                                                        write_concern=WriteConcern(w="majority", wtimeout=5000))
    count_people = 125000 #DO NOT CHANGE as it must match generate code

    # let's mass update and find (read your writes and check consistency)
    for j in range(loops):
        # pick a random record key and a random value to write
        rand_index = random.randint(0, count_people - 1)
        rand_age = random.randint(20, 50)
        if j % loopsPrint == 0:  # print every loopsPrint updates
            print('%s - process %s - records %s' % (time.strftime("%H:%M:%S"), process_id, j))
        with connection.start_session(causal_consistency=True) as session:
            # updates a document on PRIMARY and run a find if write was successful
            if (update_people(people_collection, session, process_id, rand_index, rand_age, log)):
                # finds the same document on SECONDARY
                doc = find_people(people_collection, session, process_id, rand_index, log)
                if doc is not None:
                    log_output = time.strftime("%H:%M:%S") + " - process " + str(
                        process_id) + " - index " + str(rand_index) + " - loop " + str(
                        j) + " - wrote $age=" + str(rand_age) + " read $age=" + str(doc['age']) + "\n"
                    if doc['age'] != rand_age:
                        log.put("CONSISTENCY ERROR - " + log_output)
                    elif debug:
                        log.put("OK - " + log_output)
                else:
                    log.put("DOCUMENT NOT FOUND - " + time.strftime("%H:%M:%S") + " - process " + str(
                        process_id) + " - index " + str(rand_index) + " - loop " + str(
                        j) + " - wrote $age=" + str(rand_age) + "\n")

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("You forgot the MongoDB URI parameter!")
        print(" - example: mongodb://mongo1,mongo2,mongo3/test?replicaSet=replicaTest&retryWrites=true")
        print(" - example: mongodb+srv://user:password@cluster0-abcde.mongodb.net/test?retryWrites=true")
        sys.exit(1)
    mongodb_uri = str(sys.argv[1])

    print("launching", str(processesNumber), "processes...")

    # creation of the log Queue
    queue = Queue()
    STOP_TOKEN = "STOP!!!"
    log_process = Process(target=log_queue, args=(queue, STOP_TOKEN, logFileName))
    log_process.start()

    # creation of processesNumber processes
    for i in range(processesNumber):
        process = Process(target=run, args=(i, mongodb_uri, queue))
        processesList.append(process)

    # launch processes
    for process in processesList:
        process.start()

    # wait for processes to complete
    for process in processesList:
        process.join()

    # close log file
    queue.put(STOP_TOKEN)
    log_process.join()
