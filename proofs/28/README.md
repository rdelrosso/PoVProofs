# MONITORING

__Ability to track and drill into fine-grained monitoring history to enable retrospective diagnosis of issues that have already occurred__

__SA Maintainer__: [Matt Grogan](mailto:matthew.grogan@mongodb.com) <br/>
__Time to setup__: 30 mins <br/>
__Time to execute__: 15 mins <br/>


---
## Description

This proof shows how MongoDB's management tooling in Atlas can capture and then graphically display both realtime and retrospective monitoring statistics to help administrators diagnose the cause of performance and availability issues. Both database and hardware characteristics can be correlated together in one place, to help improve the ability for administrators to identify the causes of issues and thus take remedial action to avoid these issues in the future.


---
## Setup
__1. Configure Laptop__
* Ensure MongoDB version 3.6+ is already installed your laptop, mainly to enable MongoDB command line tools to be used (no MongoDB databases will be run on the laptop for this proof)
* Ensure [nodejs](https://nodejs.org/en/) and [npm](https://www.npmjs.com/get-npm) are installed on your laptop

__2. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* Create an __M10__ based 3 node replica-set in a single cloud provider region of your choice with default settings
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Node.js version__  copy the __Connection String Only__ - make a note of this MongoDB URL address to be used later

__3. Configure Load Generator Application__
* From a terminal/shell, change directory to the __monitoring_load_app__ sub-folder of this proof and run the following to install the NPM dependency libraries required by the monitoring load generation app:
  ```bash
  npm install
  ```
* Using a text editor, modify the file __config.js__ and for the __mdb_url__ property set the value fo the __SRV Connection String__ you captured earlier (also include the password you specified for _main\_user_), for example:
  ```
  mdb_url:"mongodb+srv://main_user:MyPassword@testcluster-abcde.mongodb.net/test?retryWrites=true",
  ```

__4. Configure Key Metrics to Show in the Atlas Console__
* In the Atlas Console, click the __Metrics__ button for the deployed cluster and then in the the __Metrics__ tab, scroll to the base of the page, where the __Toggle Charts__ option is shown, and select only the following graphs to be shown in the cluster's metrics summary page, to enable database and hardware performance characteristics to be shown together:
  - Document Metrics
  - Memory
  - Op Counters
  - Disk IOPS
  - Process CPU


---
## Execution
* From a terminal/shell, in the __monitoring_load_app__ sub-folder, start the load generator application:
  ```bash
  node workloadGenerator.js
  ```

* Wait __10 minutes__ and then in the Atlas Console, for the deployed cluster, select the __.../Test Failover__ option to force a failure of the replica-set primary server (Note: the workload generator application will print out a bunch of error messages, but it should keep running). After a few minutes the console will show that the cluster's primary has changed. Wait another __5 minutes__ before beginning the _Measurement_ steps below, to enable further historical data to first be captured.


---
## Measurement
* In the Atlas Console, click the __Metrics__ button for the deployed cluster and then select the __Real Time__ tab, and then highlight that realtime cluster statistics are being displayed to help diagnose current performance issues, similar to the screenshot below:

![realtime](img/realtime.png "realtime")

* Now select the __Metrics__ tab, and point out that metrics for the previous hour (the default _zoom_ which can be changed to longer periods, such as days) are shown for a few different database and hardware related graphs together, for every member of the cluster. The result graphs show how the workload ramped-up considerably, part way through the time window shown (when the load generator app was started). These sorts of graphs, combining different historic metrics together, enable an administrator to be able to correlate retrospective database and host characteristics together simultaneously, similar to shown in the screenshot below:

![monitoring](img/monitoring.png "monitoring")

* Also point out in the monitoring results, that the failover event, resulting in one node losing its primary status and another node gaining primary status, is also captured and shown, similar to shown in the screenshot below (demarcated by the red and amber vertical bars):

![failedover](img/failedover.png "failedover")

By capturing both the occurrence of the failover event, and the characteristics of all of the cluster at the point in time of failover, administrators are more able to retrospectively determine the root cause of the failover (for example, exhaustion of storage). To drill in further, for deeper historical statistics for an individual server, the administrator can simply click on the link to just one of the servers in the cluster, to display many more metrics for the chosen time window.

