# PORTABLE

__Ability to migrate a database from one public cloud provider, to another, to avoid cloud provider lock-in, with less than 1 minute of scheduled application downtime required__

__SA Maintainer__: [Paul Done](mailto:paul.done@mongodb.com) <br/>
__Time to setup__: 30 mins <br/>
__Time to execute__: 15 mins <br/>


---
## Description

This proof shows how MongoDB can rapidly migrate data from an Atlas cluster running in one cloud provider to an Atlas cluster running in a different cloud provider, with no data loss and with only seconds of application availability interruption.

This proof uses an Atlas cluster in AWS as the original source database and a new Atlas cluster running in Azure as the new target database. The application writing into the Atlas databases will be simulated by using a load simple load generation tool, which inserts simulated _insurance customer_ records into the database.

---
## Setup
__1. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, for this user select __Add Default Privileges__ and in the __Default Privileges__ section add the roles __readWriteAnyDatabase__ and __clusterMonitor__ (make a note of the password you specify)
* Create an __M30__ based 3 node replica-set in a single AWS region of your choice, called __AWSTestCluster__, with default storage settings (backup can be disabled).
* Create an __M30__ based 3 node replica-set in a single Azure region of your choice, called __AzureTestCluster__, with default storage settings (backup can be disabled)
* In order to see the two CIDR blocks that need to be opened in the firewall for the clustes in the project, to allow the migration tool to be used later, click on the __... button__ right next to __AWSTestCluster__ deployment and choose __Migrate Data to this Cluster__. Hit __I'm ready to migrate__ and make a note of the two CIDR blocks. Don't actually attempt the migration, just close the dialog box instead
* In the Atlas Security tab, add 2 the two new __IP Whitelist__ entries for the 2 IP CIDR blocks you just captured
* In the Atlas console, __for each of the two__ database clusters, click the __Connect button__, select __Connect Your Application__, and for the __latest Node.js version__  copy the __Connection String Only__ - make a note of the two MongoDB URL addresses to be used later
* In addition, for just the source __AWSTestCluster__ deployment, click the __Connect button__ again, select __Connect Your Application__ again, but this time select the __very earliest version of Node.js__ and record the hostname of just the first primary server on your local laptop (e.g. _awstestcluster-shard-00-00-abcd.mongodb.net_) because the Migration tool used later cannot use the SRV version of a MongoDB URL

__2. Configure Laptop Environment__
* Ensure MongoDB version 3.6+ is already installed your laptop, mainly to enable MongoDB command line tools to be used (no MongoDB databases will be run on the laptop for this proof)
* Ensure Node (version 6+) and NPM are installed your laptop
* Download and install the [mgeneratejs](https://www.npmjs.com/package/mgeneratejs) JSON generator tool on your laptop
  ```bash
  npm install -g mgeneratejs
  ```

__3. Load Data Into A Collection In The Original Source Atlas Cluster__
* From a terminal window on your laptop, run the following command to generate 200 thousand, partly templated, partly randomly generated JSON documents representing insurance customer 'single view' records ingested into the __AWSTesCluster__ database
  ```bash
  mgeneratejs CustomerSingleView.json -n 200000 | mongoimport --uri "mongodb+srv://main_user:mypassword@awstestcluster-abcd.mongodb.net/test" --collection customers
  ```
 &nbsp;&nbsp;&nbsp; __Note 1__: First replace the password and address of the _AWSTestCluster_ with the values created earlier

 &nbsp;&nbsp;&nbsp; __Note 2__: The load process will take about 10 minutes to complete

    
---
## Execution

__1. Resume Loading Sample Data in the Source Cluster__
* Run the following command again to generate further insurance customer 'single view' records into the source __AWSTesCluster__ database continuously
  ```bash
  mgeneratejs CustomerSingleView.json -n 200000 | mongoimport --uri "mongodb+srv://main_user:mypassword@awstestcluster-abcd.mongodb.net/test" --collection customers
  ```
 &nbsp;&nbsp;&nbsp; __Note 1__: First replace the password and address of the _AWSTestCluster_ with the values created earlier

 &nbsp;&nbsp;&nbsp; __Note 2__: Move straight on to the next steps, so that you can show live migration whilst the source cluster is still receiving inserts

* In the Atlas console, __for each of the two__ database clusters, select the __Metrics | Collections__ tab, and check the size of the _test.customers_ database collection to show what data is currently present in each of the two clusters. There should only be data in the first cluster - __hit Refresh__ a few times for the source cluster to show that the number of documents is increasing

__2. Initiate Live Migration and Restart the Load Generator to point to the Destination Source Cluster__
* From the Atlas Console go to your target __AzureTestCluster__ deployment, hit the __... button__ and choose __Migrate Data to this Cluster__. Acknowledge the initial screen by hitting __I'm ready to migrate__. Set the following values for the fields:
    * _Hostname_: Host & port of the primary of the source _AWSTestCluster_ you recorded earlier
    * _Username_: main_user
    * _Password_: The password you set earlier
    * _Is SSL enabled?_: YES
    * _Clear any existing data on your target cluster?_: As the cluster is empty, it can be kept to NO

* Start to check the parameters by hitting the __Validate__ button. If the validation fails, double-check the hostname setting for the primary of the source AWSTestCluster deployment

* Hit __Start Migration__ and the test data is copied into the destination cluster. In the cluster overview you can see the progress of the migration. Once the initial sync is completed, the replication lag will indicate how much data still has to be migrated. 

* In the Atlas console, __for each of the two__ database clusters, select the __Metrics | Collections__ tab, and check the size of the _test.customers_ database collection to show what data is currently present in each of the two clusters. There should now be data in both the clusters - for each of the two clusters __hit Refresh__ a few times to show that the number of documents is now increasing in both clusters because the destination database is now tracking the source database

* Back in the Atlas __Cluster Overview__ for __AzureTestCluster__ wait for the initial sync to finish and for the replication lag to be shown as close to zero (e.g. just a few seconds)

* __START THE STOPWATCH__

* Stop the running _mgeneratejs_ process in the laptop's terminal window (but do NOT close the terminal window)

* In the Atlas console, for the __AzureTestCluster__ deployment, hit __Start Cutover__. 

* Back in the laptop's terminal window, change the URL used in the load generation command to now point to the target __AzureTestCluster__ and start it running again:
  ```bash
  mgeneratejs CustomerSingleView.json -n 200000 | mongoimport --uri "mongodb+srv://main_user:mypassword@azuretestcluster-abcd.mongodb.net/test" --collection customers
  ```
 &nbsp;&nbsp;&nbsp; __Note__: First replace the password and address of the _AzureTestCluster_ with the values created earlier

* __STOP THE STOPWATCH__


---
## Measurement

In the Atlas console, __for each of the two__ database clusters, select the __Metrics | Collections__ tab, and check the size of the _test.customers_ database collection to show what data is currently present in each of the two clusters. For each of the two clusters __hit Refresh__ a few times to show following:
1. the number of documents in the source __AWSTestCluster__ database is __NOT increasing__ because the load generation application is now longer pointing at it
2. the number of documents is the destination __AzureTestCluster__ database __IS increasing__ because the load generation application is now pointing at it

Record the elapsed STOPWATCH time between starting it and stopping it, which should indicate that less than a minute of scheduled downtime was required.

![collsize](img/collsize.png "collsize")

