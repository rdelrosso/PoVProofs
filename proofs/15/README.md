# PARTIAL-RECOVERY

Ability to recover a subset of data to the running live database, without requiring database or application downtime.

_SA Maintainer_: [Julien Contarin](mailto:julien.contarin@mongodb.com)


## Description

This proof item demonstrates how an administrator can recover a subset of data that has been accidentally lost from a database, using a backup copy of the database that contains the _lost_ records, back into the live database, without having to suffer any loss of service to the live database or application.

Specifically for this proof, 100 customer records will be dropped from a live Atlas database, whilst at the same time, a live application (a Python script) is continuously running against the database inserting records. The Atlas __Cloud Provider Snapshots with PITR__ feature will then be used towards a new, temporary cluster that contains the _lost_ records. The _mongoexport/import_ tools will be then be used to retrieve the 100 customer records from the temporary cluster and then restore these records back into the live Atlas database.


## Setup

__1. Configure Laptop__
* Ensure MongoDB version 3.6+ is already installed your laptop, mainly to enable MongoDB command line tools to be used (no MongoDB databases will be run on the laptop for this proof)
* Download and install the [mgeneratejs](https://www.npmjs.com/package/mgeneratejs) JSON generator tool on your laptop
  ```
  npm install -g mgeneratejs
  ```
* Ensure your laptop can run __Python 3__ and install the MongoDB Python Driver library:
  ```
  pip3 install pymongo
  ```

__2. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and then choose either to use an existing project or to create a new project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* Main cluster: Create an __M10__ based 3 node replica-set in a single cloud provider region of your choice, __changing storage size to 100 GB__, enable __Turn on Cloud Backup__ and make sure the __Continuous Cloud Backup__ flag is on.
* Temp cluster: Create an __M10__ based 3 node replica-set in a single cloud provider region of your choice, __changing storage size to 100 GB__, disable __Turn on Cloud Backup__.
* Make sure both your clusters are in the same Atlas Project, same Cloud provider and same Cloud region (NB: although feasible to PITR to a cluster in any other situation, restore time will not be as fast).
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* For the database cluster you deployed and shown in the Atlas console, click the __Connect button__, select __Connect Your Application__, select __SRV Connection String__ and choose to __Copy the SRV address__. Record this MongoDB URL address somewhere on your local laptop. This connection string will subsequently be used to load data via and then run the tests

__3. Load 100 Specific Documents Into A Collection In The Atlas Cluster__
* From a terminal/shell, generate 100 JSON documents representing insurance customer 'single view' records into the database collection __test.customers__ (these records will be deleted later on), with the following command, first replacing the password and address with the values noted earlier:
  ```
  mgeneratejs Customer360Data.json -n 100 | mongoimport --uri "mongodb+srv://main_user:MyPassword@maincluster-abcde.mongodb.net/test" --collection customers
  ```

__4. To Simulate A Live Application, Continuously Load Generic Data Into The Same Collection__
* From a terminal/shell, execute the Python script to start continuously inserting records into same database collection __test.customers__, specifying the 3 parameters for the username (*main_user*) plus the password and Atlas URL address you recorded earlier (ensure you leave this script __permanently running__), e.g.:
  ```
  ./continuous-insert.py main_user MyPassword maincluster-abcde.mongodb.net
  ```

__5. Make sure there is at least one snapshot to use PITR from__
* Navigate to the backup panel from your Main cluster on Atlas
* From the Snapshots panel: since we just created the Main cluster, it is likely that no snapshot has been taken yet. If that is the case, perform __Take snapshot now__

![snapshots](img/snapshots.png "snapshots")

* Wait for your snapshot to become available before you proceed (you will be notified by e-mail by default, should take <2 minutes).

![snapshots](img/snapshotready.png "snapshotreadysampleemail")

## Execution

__1. Show that the preexisting 100 customer records are present in the live database__
* From a terminal/shell on your laptop, launch the Mongo Shell targeting your Main Atlas cluster (change the address to match address you recorded earlier and when prompted enter your password):
  ```
  mongo "mongodb+srv://maincluster-abcde.mongodb.net/test" --username main_user
  ```
* In the Shell show that the database collection _test.customers_ contains 100 customer records, in addition to other records being continuously added:
  ```
  use test
  show collections
  db.customers.count()  // Should be greater than 100
  db.customers.find({firstname: {$exists:true}}).pretty()
  db.customers.find({firstname: {$exists:true}}).count()   // Should be 100
  db.customers.count()  // Should be greater than last time checked because new records constantly added
  ```
* Keep the Mongo Shell session connect to the Main Atlas cluster __open to for the whole duration of this exercise__ to be used in later steps


__3. Delete documents from the Main Atlas Cluster__
* Write down the time (e.g. 11:20) before you start this operation and wait for the next minute to start from your clock (e.g. wait for 11.21 to display).
* In the open Mongo Shell session, delete the **100 customer documents** from the Main Atlas database and check they have been removed:
  ```
  db.customers.remove({firstname: {$exists:true}})
  db.customers.find({firstname: {$exists:true}}).count()   // Should be zero
  db.customers.count()  // Should be greater than zero
  ```

__4. PITR to Temp Cluster__
* Navigate to the backup panel from your Main cluster on Atlas
* Select Point in Time Restore and set the date and time you wrote in Execution section 3. Do make sure you convert that time to UTC (for me, 11.20AM CEST is 9.20AM UTC):

![snapshots](img/pitrdatetime.png "pitrdatetime")

* Select Target Cluster to be the Temp Cluster:

![snapshots](img/targetcluster.png "targetcluster")

* Restore should take no more than 10 minutes (the longest is the initialization phase) leveraging DirectAttach (which requires same Atlas project, Cloud provider and Cloud region). When the restore is complete, go the next section.

__5 Retrieve copy of lost 100 customer records from queryable backup snapshot & restore these to the live database__
* In the Atlas console, for the Temp cluster, select __.../Command Line Tools__ and in the shown section __Data Import and Export Tools__ copy and record the __--host__ parameter value for use in the next step (this is required because mongoimport cannot use the _SRV_ style connection string)
* From a new terminal now run the following MongoDB import command to __export the 100 lost customer records__, changing the __--host__ field value to the one you captured in the previous step and changing the password accordingly):
  ```
  mongoexport --uri mongodb+srv://{username}:{password}@{hostname}/test --collection customers --query '{"firstname":{"$exists":true}}' --out lost_records.json
  ```

* In the Atlas console, for the Main cluster, select __.../Command Line Tools__ and in the shown section __Data Import and Export Tools__ copy and record the __--host__ parameter value for use in the next step (this is required because mongoimport cannot use the _SRV_ style connection string that you recorded earlier)
* In the same terminal, now run the following MongoDB import command to __import the 100 retrieved customer records__ back into the live database, similar to the following, changing the __--host__ field value to the one you captured in the previous step and changing the password accordingly):
  ```
  mongoimport --uri mongodb+srv://{username}:{password}@{hostname}/test --collection customers --file lost_records.json
  ```

## Measurement

In the open Mongo Shell session, re-run the query to look for the customer documents that should have been restored in the live Atlas database and verify that the __100 customer records are now present again__:
```
db.customers.count()  // Should be greater than 100
db.customers.find({firstname: {$exists:true}}).pretty()
db.customers.find({firstname: {$exists:true}}).count()   // Should be 100
db.customers.count()  // Should be greater than last time checked, 'cos new records constantly added
  ```

Also check that the _continuously inserting application_ (_continuous-insert.py_) is still running and suffered no loss of service during the whole restore execution process. This proves that partial data losses can be recovered from, without needing to take the database or application down.

## Resources

[Sample Video Demonstration](https://drive.google.com/file/d/1JEPGFUq9Yat-cZHs794CaQWJIbhIdp_K/view?usp=sharing)


