# FULL-RECOVERY-RTO

__Ability to recover a database within X minutes for a data-set size of Y GB (RTO=Xmins)__

__SA Maintainer__: [Eugene Bogaart](mailto:eugene.bogaart@mongodb.com) <br/>
__Time to setup__: 60 mins <br/>
__Time to execute__: 30 mins <br/>


---
## Description

This proof shows how the MongoDB Atlas Backup capability provides the ability to easily and quickly restore a lost or corrupted database back into a live production cluster, as part of a disaster recovery process.

As part of preparing this proof, a separate automated test framework was used to test the times for restoring specific data set sizes to different MongoDB cluster tier sizes, to attain a better understanding of what can be expected for Restore Time Objectives (RTOs). A summary of these test results is shown in the table below:

| Atlas AWS Tier             | # Shards | # Docs        | Data Size  | Restore Time |
|----------------------------|----------|---------------|------------|--------------|
| M30                        |        1 |  140 million  |  17.24 GB  |    978 secs  |
| M30                        |        2 |  140 million  |  19.24 GB  |    490 secs  |
| M40                        |        1 |  280 million  |  34.46 GB  |   1324 secs  |
| M40_NVMe                   |        1 | 1600 million  | 150.61 GB  |   9901 secs  |
| M50                        |        1 |  560 million  |  68.92 GB  |   3288 secs  |
| M60                        |        1 | 1120 million  | 137.82 GB  |   6310 secs  |
| R80			             |        1 | 3360 million  | 413.52 GB  |  18670 secs  |

_Note: The test framework that was used to obtain these figures is not required to run this proof, but you may retrieve the [RTO Framework](https://drive.google.com/drive/folders/1DhFUDu5Y8gtSbbGICxpsHNwp162_mvtY?usp=sharing) via the author of this proof - when these tests were run, some of the learned _gotchas_ and considerations were captured [here](Tips.md)_

For this proof specifically, a data set of 10 GB of uncompressed data will be uploaded to a new Atlas cluster, and with backup enabled, all the data will be deleted, to simulate a complete data loss disaster scenario. Then the Atlas restore process will be invoked, to recover all the lost data back into the same cluster, to determine the exact restore time that can be achieved. For this particular data-set on an M40 Atlas replica-set, the restore time should take approximately 300 seconds (5 minutes). _Note_, The data set used for this proof is different than the data-set used by the test framework which produced the indicative results table shown above.


---
## Setup

__1. Configure Laptop__
* Ensure MongoDB version 3.6+ is already installed your laptop, mainly to enable MongoDB command line tools to be used (no MongoDB databases will be run on the laptop for this proof)
* Ensure Node (version 6+) and NPM are installed your laptop
* Download and install the [mgeneratejs](https://www.npmjs.com/package/mgeneratejs) JSON generator tool on your laptop
  ```bash
  npm install -g mgeneratejs
  ```

__2. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* Create an __M40__ based 3 node replica-set in a single cloud provider region of your choice, __changing storage size to 400 GB__ but __DO NOT enable any backup__ as we need to enable this at a later step AFTER we have inserted some data (we will want a snapshot to exist which contains some data)
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* For the deployed cluster click the __Connect button__, select __Connect with the Mongo Shell__, and __copy__ the _SRV Connection String_
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Node.js version__  copy the __Connection String Only__ - make a note of this MongoDB URL address to be used later

__3. Load 10 GB Of Data Into A Collection In The Atlas Cluster__
* From a terminal/shell, generate 8,370,000 JSON documents representing insurance customer 'single view' records into the database collection __test.customers__ (this should result in a database of just over 10 GB of uncompressed data), with the following command, first replacing the password and address with the values noted earlier this may take an hour or so to complete):
  ```bash
  mgeneratejs Customer360Data.json -n 8370000 | mongoimport --uri "mongodb+srv://main_user:MyPassword@testcluster-abcde.mongodb.net/test" --collection customers
  ```

__4. Enable Backup And Ensure At Least One Snapshot Has Been Generated__
* In the Atlas console for the deployed cluster, select to __.../Edit Configuration__, choose to __Enable Backup__ selecting the __Continuous__ version of backup and then apply changes.
* Wait until at least 1 snapshot has been generated and is listed for the Atlas cluster similar to the screenshot below (to view go to __Backups__ in the left-hand of the Atlas console, and for the displayed cluster, in the __Options__ column select __.../View All Snapshots__)

![snapshots](img/snapshots.png "snapshots")

    
---
## Execution

__1. Delete All Data In The Database To Simulate A Disaster__
* In the Atlas Console, for the deployment, click the __Collections__ button and for the listed database __test__ (contains the _customers_ collection) click the wastebasket button, and confirm, to delete the database and its collections.
* Hit __refresh__ and confirm that the deployment contains no databases or collections now.

__2. Start The Stopwatch Used To Time Recovery__
* Start a stopwatch to simulate the fact that the Ops team have detected a disaster scenario has occurred (all data lost) and are now starting the disaster recovery process of restoring a backed-up snapshot of the database back into the Atlas cluster.

__3. Kick Off Cluster Restore Process From Backup Snapshot__

* In the left hand side of Atlas Console, select __Backup__, then for the displayed cluster, in the Options column select .../View All Snapshots, and for the _most recent snapshot_ listed, click __Restore or Download__ as shown below:

![snapshots-restore](img/snapshots-restore.png "snapshots-restore")

* Select the option __Choose cluster to restore to__ as shown below:

![restore-option](img/restore-option.png "restore-option")

* Choose to restore to the existing running Atlas cluster that incurred the disaster with all its data deleted, and click __Restore__ as shown below:

![restore-finalise](img/restore-finalise.png "restore-finalise")

* In the summary page shown, check the details and then click __Confirm & Continue__ as shown below:

![restore-confirm](img/restore-confirm.png "restore-confirm")

* The resulting Atlas console will now show the deployment with status "_We are deploying your changes_" as shown in the screenshot below. __Keep refreshing__ the browser view until the status of the deployment is shown as active again, indicating that the backup should have restored.

![waiting](img/waiting.png "waiting")

* In the Atlas Console, for the deployment, click the __Collections__ button and select the listed database __test__ which should now have reappeared - confirm that this contains the collection __customers__ and there are _8370000_ records listed for the collection of data size _10 GB_, which indicates that the backup restore process has been successful

__4. Stop The Stopwatch Used To Time Recovery__
* Stop the stopwatch and record the time that was taken to perform a full restore of all data from backup. This time is the RTO achieved (Restore Time Objective).

 
---
## Measurement

The __recorded stopwatch time__ will indicate the __Restore Time Objective (RTO) achieved__ for recovering the whole data set into a live cluster. For the sample data-set and Atlas tier used in this proof, this duration should be approximately 5 minutes (300 seconds). To confirm that the restoration process has completed successfully, from the __Collections__ tab of the Atlas Console for the deployed cluster, you should see that all the lost data has been restored, similar to the screenshot below:

![collection-list](img/collection-list.png "collection-list")

