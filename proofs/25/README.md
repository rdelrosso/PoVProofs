# PERF-ADVICE

__Ability to continuously be informed with database performance improvement advice for long running databases, enabling database health to be proactively maintained__

__SA Maintainer__: [Marc Martin](mailto:marc.martin@mongodb.com) <br/>
__Time to setup__: 60 mins <br/>
__Time to execute__: 15 mins <br/>


---
## Description

This proof shows how the Atlas Performance Advisor can automatically suggest to users when and how to create indexes based on its automated observation of real database load, to improve the performance of the running application. This capability is especially useful for long lived applications where the size and nature of the underlying data set and the types of typical queries run, change over time.

For this proof, one million randomly generated _insurance customer single view_ records are loaded into the database and then a non-optimised query is run a number of times to enable the Performance Advisor to detect this common non-optimal query and hence suggest how to remedy the performance issue, from within Atlas Performance Advisor tab. __Note:__ The data load process will take about 0.5 to 1 hour to complete. Showing the proof item (Execution section below) can take 10 to 20 minutes.


---
## Setup

__1. Configure Laptop__
* Ensure MongoDB version 3.6+ is already installed your laptop, mainly to enable MongoDB command line tools to be used (no MongoDB databases will be run on the laptop for this proof)
* Ensure Node (version 6+) and NPM are installed your laptop
* Download and install the [mgeneratejs](https://www.npmjs.com/package/mgeneratejs) JSON generator tool on your laptop
  ```bash
  npm install -g mgeneratejs
  ```

__2. Configure Atlas__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* Create an __M10__ based 3 node replica-set in a single cloud provider region of your choice with default settings (__Note:__ this PoV probably won't working on M20 or higher)
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Node.js version__  copy the __Connection String Only__ - make a note of this MongoDB URL address to be used later

__3. Load Data Into A Collection In The Atlas Cluster__
* Generate 1 million, partly templated, partly randomly generated JSON documents representing _insurance customer single view_ records. Ensure the collection does not already exist, or choose a different name. 
  ```bash
  mgeneratejs CustomerSingleView.json -n 1000000 | mongoimport --uri "mongodb+srv://main_user:mypassword@democluster-abcd.mongodb.net/test" --collection customers --numInsertionWorkers=10
  ```
 &nbsp;&nbsp;&nbsp; __Note 1__: First replace the password and address with the values created earlier

 &nbsp;&nbsp;&nbsp; __Note 2__: The load process will take nearly an hour to complete

__4. Check That The Collection's Data Can Be Accessed Using the MongoDB Shell__
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect with the Mongo Shell__, and in the __Run your connection string in your command line__ section copy the connection command line - make a note of this connection command line to be used later
* Open a terminal window and use the copied connection string to use the Mongo Shell to connect to the database with the user/password created in step 1.
  ```bash
  mongo "mongodb+srv://democluster-abcd.mongodb.net/test" --username main_user
  ```
* Inside the Mongo Shell, move to the _test_ database and execute a simple query to quickly test that the 1 million records are visible.
  ```js
  use test
  db.customers.find().count()
  ```
The count should show the number of imported documents (1000000).
__Note 1:__ Make sure that Performance Advisor is empty before you begin. You can delete any unwanted old advice by pausing and resuming the cluster.
__Note 2:__ If you ran through the preparation above to this point, you now can pause the cluster and resume once you are at the customer to present the Execution below.
    
---
## Execution

To induce the Performance Advisor into identifying an inefficient query and to suggest an index to apply, some JavaScript looping and collection updating code will be run that contains a complex query as part of the update, which is not backed by an index, and hence will be flagged as slow.

From the existing Mongo Shell session, execute the following code to add a risk score to the life insurance contract of all smoking female customers that are born in 1990, across the 1 million record-set:
  ```js
  for (i=1; i<=10000; i++) {
     start = new Date().getTime();
     db.customers.update({
        'region': i, 
        'address.state': 'UT', 
        'policies': {$elemMatch: {'policyType': 'life', 'insured_person.smoking': true}},
        'yob': {$gte: ISODate('1990-01-01'), $lte : ISODate('1990-12-12')},
        'gender': 'Female' 
     },
     { $set: { "policies.$[elem].risk" : 300 } },
     {
        multi: true,
        arrayFilters: [ { "elem.policyType": "life" } ]
     });
     print(i, ". time (ms): ", ((new Date().getTime())-start));
  }
  ```
Wait until the looping query/update workload has at least executed once (ie. the counter value _1_ appears in the Shell output). Also notice the time deltas output in the Shell, which show how long each update has taken (make a rough note of how long these gaps tend to be). __Note:__ Although this is not a first meeting demo, some might want to fill the waiting time (approx. 5 minutes) by i. e. moving to the Real Time dashboard of the cluster to show collection activity, scanned objects metric or cpu utilization. It might be a good advice to clarify with the customer that these activities are not related to this Performance Advisor proof item.


---
## Measurement

Go to the Atlas console, and for the test database cluster navigate to the __Performance Advisor__ tab. When the counter in the Shell is up to around 25-50 or so (i.e. after waiting a few minutes), the Performance Advisor should show this identified slow query and provide an index suggestion.

![query](img/pa.png "performance advisor")

Next, to the create the suggested index, click on __More Info__ which gives the suggested command to create the index, then copy this commend which should be similar to the following:
  ```js
  db = db.getSiblingDB("test")
  db.getCollection("customers").createIndex({
     "region": 1,
      "address.state": 1,
      "gender": 1,
      "yob": 1
  }, {background: true})
  ```
Interrupt the query in the Mongo Shell (_Ctrl-C_). Then in the Shell execute the _createIndex_ command given by the Performance Advisor above. Then re-run the Javascript looping code from earlier and you will see this is now executing much faster (in the Shell output, look at the deltas printed in with a timestamp in milliseconds and notice that the deltas between updates are now much smaller in time). 

Essentially, a missing index will have been automatically suggested by the Performance Advisor based on real database load. You will have shown that by then applying the recommended index, the performance of that real load database queries was improved greatly.

