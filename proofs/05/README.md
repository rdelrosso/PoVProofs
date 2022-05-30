# WORKLOAD-ISOLATION

__Ability to execute aggregations on the same cluster as CRUD operations are currently occurring, with appropriate performance workload isolation__

__SA Maintainer__: [Ben Perlmutter](mailto:benp@mongodb.com) <br/>
__Time to setup__: 45 mins <br/>
__Time to execute__: 30 mins <br/>


---
## Description

This proof shows how MongoDB can isolate workloads on the same cluster as aggregations and CRUD operations are currently occurring, with appropriate performance for each set of operations.

The proof first generates 1m random documents adhering to the schema defined in the file _CustomerSingleView.json_ using the _mgenerate_ tool. It then steps through the process of loading this data into MongoDB Atlas, and then provides two scripts. The first script will update 1k documents approximately every second against the primary node of the database. The second script will send an aggregation framework query to the nodes tagged for ANALYTICS. After running the two scripts for a period of time, it will be clear in the Metrics section of Atlas that the two workloads are completely isolated from each other.

---
## Setup
__1. Configure Laptop__
* Ensure MongoDB version 3.6+ is already installed your laptop, mainly to enable MongoDB command line tools to be used (no MongoDB databases will be run on the laptop for this proof)
* Ensure Node (version 6+) and NPM are installed your laptop
* Download and install the [mgeneratejs](https://www.npmjs.com/package/mgeneratejs) JSON generator tool on your laptop
  ```bash
  npm install -g mgeneratejs
  ```
* Ensure Python 3 is installed and install required Python libraries:
  ```bash
  pip3 install pymongo
  pip3 install dnspython
  ```
__2. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* Create an __M30__ based 3 node replica-set in a single cloud provider region of your choice with 3 regular Electable nodes and at least 2 __Analytical Nodes__ (to ensure the _analytics_ nodes are highly available too) as show in the screenshot below
![Analytics Nodes](img/analytics_nodes.png "Analytics Nodes")
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Node.js version__  copy the __Connection String Only__ - make a note of this MongoDB URL address to be used later

__3. Load Data Into A Collection In The Atlas Cluster__
* In a new terminal/shell from the base folder of this proof, run the following command to generate 1 million, partly templated, partly randomly generated JSON documents representing insurance customer 'single view' records into the database collection _acme\_inc.customers_
  ```bash
  mgeneratejs CustomerSingleView.json -n 1000000 | mongoimport --uri "mongodb+srv://main_user:MyPassword@testcluster-abcde.mongodb.net/acme_inc" --collection customers
  ```
 &nbsp;&nbsp;&nbsp; __Note 1__: First replace the password and address with the values captured earlier

 &nbsp;&nbsp;&nbsp; __Note 2__: The load process will take nearly an hour to complete. You can verify the data loaded by going to your Atlas cluster and view it in the data explorer (via the **Collections tab**)

__4. View the Replica Set Topology__
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect with the Mongo Shell__, and in the __Run your connection string in your command line__ section copy the connection command line - make a note of this connection command line
* In a new terminal/shell from the base folder of this proof, paste in the connection string you just copied and before pressing enter, add the path of a Mongo Shell script to be run (_./print\_repset_conf.js_) which will print a summary of the cluster's replica-set configuration (providing the password you specified earlier, when prompted for), for example:
  ```bash
  mongo "mongodb+srv://testcluster-abcde.mongodb.net/test" --username main_user ./print_repset_conf.js
  ```
&nbsp;The output should show that of the 5 replicas, __2 of them are tagged for ANALYTICS__, similar to the screenshot below

![Replica Set Configuration](img/repset_conf.png "Replica Set Configuration")

    
---
## Execution
* In one terminal/shell from the base folder of this proof, run the __update__ script to perform a continuous operational/transactional workload (applying random updates to documents) against the cluster, indefinitely, ensuring you provide the full application SRV connection string you copied during the setup for this proof, for example (ensure you change the password to the value you provided):
  ```bash
  ./update_docs.py "mongodb+srv://main_user:MyPassword@testcluster-abcde.mongodb.net/test?retryWrites=true"
  ```

&nbsp;This update workload should be executed against the cluster's current primary node

* In a separate terminal/shell from the base folder of this proof, run the __query__ script to perform a continuous analytical workload (performing aggregation framework group-bys) against the cluster, indefinitely, ensuring you provide the full application SRV connection string you copied during the setup for this proof, for example (ensure you change the password to the value you provided):
  ```bash
  ./query_docs.py "mongodb+srv://main_user:MyPassword@testcluster-abcde.mongodb.net/test?retryWrites=true"
  ```

&nbsp;This query workload uses a __read preference tag__ targeting the 2 secondary nodes that are marked for __analytics__
 

---
## Measurement
After a minimum of __10 minutes__, navigate to the __Metrics__ tab of the Atlas console for the deployment and select to view the `Query Targeting`, `Query Executor` and `Scan & Order` metrics for the members of the cluster together. As shown in the screenshot below, you should see that only the _Analytics_ nodes are targeted with the aggregation queries, with the three remaining _Electable_ replicas not processing the aggregation workload at all. Note: Depending on screen resolution, the Atlas UI may not show all of the 5 nodes at a time so you may need to check/un-check the __Toggle memebers__ in the UI, to get a view of each of the replicas.

![Metrics](img/metrics.png "Metrics")

