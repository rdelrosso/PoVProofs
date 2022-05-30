# CONSISTENCY

__Ability to enforce strong consistency across a distributed database, to ensure applications always see the most up to date data__

__SA Maintainer__: [Rohan Walia](mailto:rohan.walia@mongodb.com) <br/>
__Time to setup__: 30 mins <br/>
__Time to execute__: 30 mins <br/>


---
## Description

This proof shows how MongoDB supports strongly consistent reads and writes in a sharded environment even when reading from secondaries.

The proof uses randomly generated persons data (people records each with _firstname_, _lastname_, _age_, _addresses_ and _phones_ fields, plus other fields). The main test continuously updates the _age_ field of random people via replica-set primaries and then reads the _age_ field value back for each corresponding updated person records via the replica-set secondary, verifying that the values match each time. The following MongoDB driver settings are used: _writeConcern:majority_, _readConcern:majority_, _readPreference:secondaryPreferred_, _retryableWrites:true_, _causal consistency enabled_. During the test run, a failover is induced via the Atlas _Test Failover_ feature to check that strong consistency is still achieved, even when servers fail.

 _About the run environment_: This proof requires high read and write rate. It's strongly advised that all scripts are executed in an AWS EC2 VM running in the same region as your ATLAS Cluster.

---
## Setup
__1. Configure Laptop__
* Ensure MongoDB version 3.6+ is already installed your laptop, mainly to enable MongoDB command line tools to be used (no MongoDB databases will be run on the laptop for this proof)
* Ensure __Python 3__ is installed and install required Python libraries:
  ```bash
  pip3 install faker pymongo dnspython
  pip3 install certifi
  ```

__2. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Atlas Admin__ (make a note of the password you specify)
* Create an __M30__ based sharded cluster, with __4 Shards__ with __3 replicas per shard__ in a single cloud provider region of your choice, close to your current location, with default settings
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect with the Mongo Shell__, and in the __Run your connection string in your command line__ section copy the connection command line - make a note of this connection command line to be used later

__3. Configure a Sharded Database Collection__
* From a terminal/shell, launch the Mongo Shell against the database cluster by running the following command (changing the host MongoDB URL address and providing the password, when prompted, with the values you recorded earlier):
  ```bash
  mongo "mongodb+srv://testcluster-abcd.mongodb.net/test" --username main_user
  ```
* From the Mongo Shell session, run the following commands to crate a sharded database _world_ containing a sharded collection _people_ with pre-split chunks to help promote an even balance of chunks across all shards when the data is later loaded into the collection:
  ```js
  use world
  sh.enableSharding('world')
  sh.shardCollection('world.people', {'process': 1, 'index': 1})
  sh.splitAt('world.people',{'process':2,'index':1250})
  sh.splitAt('world.people',{'process':4,'index':1250})
  sh.splitAt('world.people',{'process':6,'index':1250})
  sh.status()
  ```
&nbsp;&nbsp;NOTE: The output of the last command run above should show that chunks are evenly spread out over all 4 shards

__4. Generate 1 Million Sample Records__
* From a terminal/shell, execute the script to generate and load 1 million randomly generated documents into the collection __world.people__ evenly spread across the 4 shards (changing the host MongoDB URL address and providing the password, when prompted, with the values you recorded earlier)
  ```bash
  ./generate1Mpeople.py "mongodb+srv://main_user:PASSWORD@testcluster-abcd.mongodb.net/test?retryWrites=true"
  ```

&nbsp;&nbsp; _NOTE_: The data load process will take about 5-10 minutes to complete. __It is necessary to let the 1M documents load process to completed finish before moving to _Execution_ phase, otherwise the proof will not work correctly__.


---
## Execution
The execution script to be run will launch 8 processes, each running the same loop continuously performing the actions: 1) update the _age_ field of 1 document randomly via a replica-set primary, 2) read the _age_ field from the same document via a replica-set secondary, 3) verify that read value is the same as the original written value, 4) log the result in __consistency.log__

* Run the main script to continuously perform the updates and check them (changing the host MongoDB URL address and providing the password, when prompted, with the values you recorded earlier):
  ```bash
  ./updateAndCheckPeople.py "mongodb+srv://main_user:PASSWORD@testcluster-abcd.mongodb.net/test?retryWrites=true"
  ```
 
* Whilst the script is running, via the Atlas console, for the deployed cluster, choose the option __Test Failover__ and observe the script's console console output. The script will detect when the primaries are changing due to election, issue some warning messages and simply retry the read, similar to the following output:
  ```
  15:34:42 - process 4 - records 670
  15:34:43 - process 2 - records 550
  not master
  testcluster-shard-03-01-abcd.mongodb.net:27016: The read operation timed out
  testcluster-shard-03-01-abcd.mongodb.net:27016: Write results unavailable
  testcluster-shard-01-02-abcd.mongodb.net:27016: [Errno 111] Connection refused
  15:34:45 - process 6 - records 630
  ```

The connection errors are due to reads and writes being stopped during the short failover


---
## Measurement

The logged consistency log file should contain only successful results showing that no consistency issues were detected, with content similar to the following (run `head consistency.log` to view):
  ```
  OK - 10:33:33 - process 5 - index 71765 - loop 37 - wrote $age=29 read $age=29
  OK - 10:33:33 - process 2 - index 71441 - loop 37 - wrote $age=39 read $age=39
  OK - 10:33:33 - process 6 - index 41054 - loop 40 - wrote $age=46 read $age=46
  ```

To check that no consistency issues were detected, run the following command:
  ```bash
  grep CONSISTENCY consistency.log 
  ```

If there are no consistency issues the output should show no results. If there are consistency issues, errors will be logged similar to:
  ```
  CONSISTENCY ERROR - 15:34:44 - process 6 - index 1568 - loop 628 - wrote $age=43 read $age=55
  ```

To see when replica-set elections occurred, run the following command:
  ```bash
  grep READ consistency.log 
  ```

The output should include warnings similar to the following:
  ```
  READ ERROR - 10:36:24 - process 6 - index 92399
  READ ERROR - 10:36:24 - process 3 - index 86666
  ```

This is a sample of `consistency.log` during a failover:
  ```
  OK - 10:36:24 - process 6 - index 52289 - loop 4380 - wrote $age=35 read $age=35
  OK - 10:36:24 - process 7 - index 76599 - loop 4416 - wrote $age=33 read $age=33
  WRITE ERROR - 10:36:24 - process 7 - index 107548 - age 24
  OK - 10:36:24 - process 2 - index 34486 - loop 4328 - wrote $age=25 read $age=25
  OK - 10:36:24 - process 4 - index 105678 - loop 4363 - wrote $age=27 read $age=27
  OK - 10:36:24 - process 0 - index 99337 - loop 4322 - wrote $age=31 read $age=31
  OK - 10:36:24 - process 3 - index 32165 - loop 4382 - wrote $age=35 read $age=35
  READ ERROR - 10:36:24 - process 6 - index 92399
  DOCUMENT NOT FOUND - 10:36:24 - process 6 - index 92399 - loop 4381 - wrote $age=20
  OK - 10:36:24 - process 5 - index 105865 - loop 4303 - wrote $age=26 read $age=26
  WRITE ERROR - 10:36:24 - process 5 - index 61415 - age 49
  OK - 10:36:24 - process 1 - index 29321 - loop 4331 - wrote $age=41 read $age=41
  OK - 10:36:24 - process 4 - index 21685 - loop 4364 - wrote $age=27 read $age=27
  ```

Note: On how to show example of inconsistency see [separate doc](show_inconsistency.md)

