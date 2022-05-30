# CHANGE-CAPTURE 

__Ability for applications to listen for and react to individual database events, in realtime (e.g. for fraud detection for updating a realtime visual dashboard or for CDC capture for downstream systems)__

__SA Maintainer__: [Blaine Mincey](mailto:blaine.mincey@mongodb.com) <br/>
__Time to setup__: 15 mins <br/>
__Time to execute__: 30 mins <br/>


---
## Description
This proof shows how MongoDB can be utilized to easily implement CDC (Change Data Capture) by using the native Change Streams capability within MongoDB. Change Streams allows applications to access realtime data changes without the complexity and risk of tailing the oplog of each individual shard, and the challenges of trying to reconcile ordering across these. Applications can use Change Streams to subscribe to all data changes on a single collection, a database, or an entire deployment, and immediately react to them. Applications can also filter for specific changes or transform the notifications at will.

In order to illustrate this capability, we will run several different Python scripts to listen for several distinct CRUD style operations executed against a MongoDB cluster running in Atlas. Specifically, we will run a multi-threaded Python 'listener' process that will show how specific types of changes can be listened to for a specific collection and reacted to in different ways (i.e. for Insert, Update, Delete, and Replace operations). Also, we will illustrate how a Change Stream can be interrupted and then resumed without missing a single change.


---
## Setup
__1. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* Create an __M10__ based 3 node replica-set in a single cloud provider region of your choice with default settings
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Python version__  copy the __Connection String Only__ - make a note of this MongoDB URL address to be used later

__2. Configure Laptop Environment__
* [Download](https://www.mongodb.com/download-center/compass) and install Compass on your laptop
* Ensure your laptop can run __Python 3__ and then install the MongoDB Python Driver library, __pymongo__, e.g.:
  ```bash
  pip3 install pymongo python-dotenv dnspython Faker
  ```
* Rename the file _.env.example_ to _.env_ (run `ls -a` in the proof's base directory to see these files) - this file contains a number of variables:
    * NUM_RECORDS_TO_GENERATE - Defaults to 100 for the insert script
    * DATABASE - Name of the database that is defaulted to 'bankdatabase'
    * COLLECTION - Name of the collection that is defaulted to 'accounts'
    * MONGODB_ATLAS_URL - The URL to your MongoDB Atlas cluster
* In the file  _.env_ change the value of the __MONGODB_ATLAS_URL__ variable to the __Atlas Cluster SRV address__ you recorded earlier, setting the password to the value you specified earlier for _main\_user_, for example:
  ```
  MONGODB_ATLAS_URL = mongodb+srv://main_user:MyPassword@testcluster-abcd.mongodb.net/test?retryWrites=true
  ```

__3. Execute Script to Create Database & Collection Ready to be Listened to__
* Via a terminal/shell in the base directory for this proof, run the following script to create the database and collection (_bankdatabase.accounts_) as this must exist prior to starting a change stream:
  ```bash
  ./reset.py
  ```

### Start Change Stream Listener
* Run the following script to start the Change Streams Listener script which will spawn separate listener threads for the different types of event handlers to be proved (i.e. for inserts, updates, deletes, replaces, plus a simulated failure event which will cause a resume to be proved):
  ```bash
  ./change_stream_listener.py
  ```

The output of running the script should look similar to the following:

![](images/change_stream_start.png)

This script should indicate that a change stream listener has started for Insert, Update, Delete, and Replace events along with the filter to simulate a failure and a subsequent resume.


---
## Execution
    
### TEST 1: Insert Event
Open a separate terminal and run the [insert_bank_account_data.py](insert_bank_account_data.py) script
  ```bash
  ./insert_bank_account_data.py
  ```

While it is running, you should see output similar to the following indicating that bank records are being inserted:

![](images/insert.png) 

While the insert script is running, check the terminal for the change stream output which should look like the following:

![](images/insert_cs.png)

The Insert event is filtered for any bank customers inserted into the accounts collection with a negative checking account balance.

After performing a number of inserts the _insert\_bank\_account\_data.py_ process finishes

### TEST 2: Update Event

Next, we will test the update change stream functionality by running the [update_bank_account_data.py](update_bank_account_data.py)
  ```bash
  ./update_bank_account_data.py
  ```

As this is run, the output should look like the following:

![](images/update.png)

As indicated, the script is filtering for checking accounts with under $1000 in the balance and adding $100 to it.

As the script is running, check the terminal where the change stream listener is running and the output should be similar to the following:

![](images/update_cs.png)

The Update event is being filtered for bank customers where their checking account has a deposit made and indicating the new balance.

After performing a number of updates the _update\_bank\_account\_data.py_ process finishes

### TEST 3: Delete Event

Next, we will test the delete change stream functionality by running the [delete_bank_account_data.py](delete_bank_account_data.py)
  ```bash
  ./delete_bank_account_data.py
  ```

As this script is executing, you should see the following in the terminal:

![](images/delete.png)

The delete script is deleting customers with a negative checking account balance.

As the delete script is running, check the terminal output for the change stream listener and you should find similar output to the following:

![](images/delete_cs.png)

After performing a number of deletes the _delete\_bank\_account\_data.py_ process finishes

### TEST 4: Replace Event

Next, we will test the replace change stream functionality by utilizing the use of MongoDB Compass. It should be noted the when an update to a document is made using MongoDB Compass, a full document replace occurs. Connect to your MongoDB Atlas Cluster using MongoDB Compass (the Atlas console has a _Connect_ option for Compass to copy the Compass settings into your clipboard) and find open the existing documents in the database we are using (in collection _bankdatabase.accounts_). Locate a random document in the collection and make a few updates to it and then click 'Update'. This should look similar to what is shown here:

![](images/compass_replace.png)

After you have clicked the 'Update' button, check the terminal output for our change stream listener.  If you made updates to a single document, there will only be a single entry in the terminal.  You should see output similar to this:

![](images/replace_cs.png)

 
### TEST 5: Resume Capability

For our final execution of the proof, we will test the resume capability of change streams. This is a critical aspect of MongoDB Change Streams as it provides
the capability of not losing any changes and being able to resume immediately following the last change event.

__Important__: Do NOT stop the _change\_stream\_listener.py_ process is this is still required.

Start the [resume_update_data.py](resume_update_data.py) script
  ```bash
  ./resume_update_data.py
  ```

The output should be similar to the following:

![](images/resume.png)

This script is scanning thru the collection's documents filtering for customers with a checking account balance greater than $1000. For these records, an additional field named 'resumeCounter' is added to the specific document and increased by 1 so we can verify if we missed any records (purely so we can check our proof works) as we are going to terminate the change stream and then restart it.

Inspect the output of the change stream terminal, you should see something similar to the following:

![](images/resume_cs.png)

It should be noted that for every 5 updates, the original change stream listener will simulate a 10 second failure while the [resume_update_data.py](resume_update_data.py) is running.  After 10 seconds, the resume change stream is closed and then reestablished using the resume token. Take note of the 'Counter Value' value as this is being incremented by 1. You should see, for example, in the image above, the Counter Value is 5 when a failure is indicated.  Once the change stream restarts, the Counter Value starts at 6 as expected. The change listener is not missing any records even though the change stream is closed and is then reestablished 10 seconds later because it uses the resume token to start from where it last was, catching up on any missed changes which occurred when it was unavailable for 10 seconds.

You can do a quick inspection using MongoDB Compass to ensure that no increments of the 'resumeCounter' field were lost during the failure simulations by doing something similar to this:

![](images/compass_spotcheck.png)

Simply filter within MongoDB Compass for documents with the 'resumeCounter' field that is greater than 0, sort by 'resumeCounter' ascending, and then project only the 'resumeCounter' field.


---
## Measurement

For each of the tests, the following changes should have been detected and shown in the output console for the __change_stream_listener.py__ process:

* __TEST 1__: Insert events detected and displayed
* __TEST 2__: Update events detected and displayed
* __TEST 3__: Delete events detected and displayed
* __TEST 4__: One replace event detected and displayed
* __TEST 5__: Monotonically increasing counter values displayed with no gaps, even when intermittent simulated failure events occur and are shown

