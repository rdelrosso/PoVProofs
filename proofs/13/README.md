# FULL-RECOVERY-RPO

__Ability to recover a database to a specific point in time with zero data loss (RPO=0)__

__SA Maintainer__: [Jay Runkel](mailto:jay.runkel@mongodb.com) <br/>
__Time to setup__: 15 mins <br/>
__Time to execute__: 30 mins <br/>


---
## Description

This proof shows how MongoDB Atlas Continuous Backup provides point-in-time recovery with zero data loss. This is demonstrated by simulating the corruption of a database due to a program error and then restoring the database to the last known good point. The following steps are performed:
* An initial set of "good" documents are loaded into MongoDB
* The current time is noted
* A set of corrupt documents are loaded into MongoDB
* The Atlas backup/restore capabilities is used to restore the database to the point in time before the corrupt documents were loaded
 
---
## Setup
__1. Configure Laptop__
* Ensure MongoDB version 3.6+ is already installed your laptop, mainly to enable MongoDB command line tools to be used (no MongoDB databases will be run on the laptop for this proof)
* [Download](https://www.mongodb.com/download-center/compass) and install Compass on your laptop
* Ensure Node (version 6+) and NPM are installed your laptop
* Download and install the [mgeneratejs](https://www.npmjs.com/package/mgeneratejs) JSON generator tool on your laptop
  ```bash
  npm install -g mgeneratejs
  ```

__2. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* Create an __M10__ based 3 node replica-set in a single cloud provider region of your choice and __ensure Continuous Backup is Enabled__
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Node.js version__  copy the __Connection String Only__ - make a note of this MongoDB URL address to be used later

    
---
## Execution

Execute the following steps during the demonstration:

__1. Load the "good" documents (1000 documents)__
  ```bash
  date; mgeneratejs mgenerateBefore.json -n 1000 | mongoimport --uri "mongodb+srv://admin:MyPassword1@democluster-abcde.mongodb.net/test" --collection RPO; date
  ```
	
Before running, change the password and address to match the ones you recorded earlier. All these documents will have a docType field whose value is “BEFORE_CORRUPTION"

__2. Create backup snapshot (if necessary)__
* From the top-level cluster view, navigate to the Backup tab by pressing the "Metrics" button and then selecting the "Backup" tab
* Review the list of snapshots. If at least one is listed, you are done.
* If there are no backup snapshots listed, press the "Take Snapshot Now" and use "Good Snapshot" as the description for your snapshot. Press the "Take Snapshot " button and wait for the snapshot to complete.


__3. Corrupt the collection__

Load a 100 “bad” documents into the same collection
  ```bash
  date; mgeneratejs mgenerateAfter.json -n 100 | mongoimport --uri "mongodb+srv://admin:MyPassword1@democluster-abcde.mongodb.net/test" --collection RPO
  ```

Before running, change the password and address to match the ones you recorded earlier. All these documents will have a docType field whose value is “AFTER_CORRUPTION"

__4. Perform a point-in-time restore in Atlas by:__

  1. Selecting the “Metrics" button on your cluster pane
  2. Selecting the "Backup" tab
  3. Select “POINT IN TIME RESTORE” button
  4. Enter today's date. (If you click in the date box a calendar widget will appear)
  5. Enter the time from step #2. You may need to convert to the correct time zone.
  6. Press the "Next:Select Cluster” button and select the current cluster.

 
---
## Measurement

Once the restore is complete, validate the results by using Compass (or the Atlas Collection Browser) to show:
* The total number of documents in the collection is 1000
* All the documents in the collection have {docType: “BEFORE_CORRUPTION”}
* None of the documents in the collection have  {docType: “AFTER_CORRUPTION”}

