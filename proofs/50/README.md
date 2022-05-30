# MULTI-CLOUD

__Ability to deploy a distributed database across multiple cloud providers in multiple regions, with automated failover, for maximum high availability__

__SA Maintainer__: [Girish Dusane](mailto:girish.dusane@mongodb.com) <br />
__Time to setup__: 15 mins <br />
__Time to execute__: 10 mins

---
## Description
This proof shows that a MongoDB Atlas database cluster can be deployed across 3 separate cloud providers, for maximum high availability. To prove this, by switching the highest priority region for a deployment, another member of the replica set, hosted with a different cloud provider, is automatically promoted to primary. The client application's MongoDB driver detects this primary host change and automatically fails over. This provides extra resiliency protection for users who have a multi-cloud strategy and want to have their data available with different cloud providers. 

For this proof, we are leveraging two behaviors of MongoDB and the 4.2-compatible drivers:

1. The primary is the only member in the replica set that receives write operations
2. The official MongoDB 4.2-compatible drivers enable Retryable Writes by default

A Node.js application continuously inserts randomly generated documents into the database collection _test.records_. When the application detects a change in the primary node due to the switching of priorities in region, it silently performs a **retryable write** to continue with the inserts. During the proof, you will change the priority of the regions to the Cloud Provider of your choice. When you change the Highest Priority provider and/or region in an active multi-region cluster, Atlas performs a rolling restart on all nodes in that cluster. This change triggers an election. The result selects a new primary node in the provider and region specified. Atlas doesn’t need to perform an initial sync or re-provision hosts when changing this configuration, enabling easy demonstration uninterrupted continuous write operations while switching Cloud Providers.

This proof is similar to proof [18 - MULTI-REGION-HA](../18). In that proof, we used "Test Failover" to simulate a node going down, here we will switch priority and "force" the writes to hit a node that is hosted with a different Cloud Provider.


---
## Setup
__1. Configure Laptop__
* Ensure Node (version 6+) and NPM are installed your laptop
  
* From the root folder of this proof, at the command line install all the dependencies listed in package.json
  
  ```bash
  npm install
  ```

__2. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* Create an __M10__ based 3 node replica-set, setting the __Multi-Cloud, Multi-Region & Workload Isolation__ toggle to __YES__ and placing each 1 of the 3 replicas in a different cloud provider of your choice (e.g. _AWS us-west-1, GCP us-west2, Azure westus_)
* In the Security tab, add a new __IP Access List__ for your laptop's current IP address
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Node.js version__  copy the __Connection String Only__ - make a note of this MongoDB URL address to be used later


---
## Execution
* From a terminal/shell, execute the Node.js script to start continuously inserting records into the Atlas deployed database collection __test.records__, specifying the 3 parameters for the username (*main_user*) plus the password and hostname from the Atlas URI string you recorded earlier, e.g.:
  ```
  node app mongodb+srv://main_user:password@testcluster.bxmed.mongodb.net/test/
  ```

* View the terminal/shell output of the Node.js script to check it has successfully connected to the Atlas database and is reporting that records are being inserted

* From the Atlas console, select the __.../Edit Configuration__ option and select the __Cloud Provider & Region__ card to show the electable nodes. You can then drag and drop any one of the bottom rows to the first row of your cluster's Electable Nodes, similar to the example below:

![changepriority](img/changepriority.gif "changepriority")

* Click on the green __Review Changes__ button to review and apply the configuration change.
* After this change, Atlas performs a rolling restart on all nodes and elects a new **PRIMARY**
* Back in the terminal/shell continuous output, keep visually scanning the output looking for the change in the IP address and region that the last insert took place in. _Note_: It __may take a few minutes__ before your newly __HIGHEST__ priorty region is elected as the PRIMARY node.
* You will see a blip in the cadence of the inserts that demonstrate that the Retryable Writes feature successfully connected you to a new host in a different Cloud Provider
* ADDITIONAL TASK: You can include the connection string to include write majority but please remember to add quotes to your connection string

```
node app "mongodb+srv://main_user:password@testcluster.bxmed.mongodb.net/test?w=majority"
```


---
## Measurement

After changing your cluster's __Highest Priority__ provider and region, you should be able to see exactly when the script started writing to a different host in a different Cloud Provider:

![failover](img/failover.png "failover")

The time taken when the failover happened is NOT the time it took for primary to be elected. That is how long it took for the driver to connect to the old primary, get an error and then retry the write.

Since the documents have a field called `documentNumber` that increases monotonically with each document that is written, you can also view the collection to show that no writes were lost during the switch from one Cloud Provider to another.

![collection](img/collection.png "collection")
