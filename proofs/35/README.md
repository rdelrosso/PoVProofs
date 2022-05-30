# SAFE-WRITES

__Ability to guarantee that critical insert/update/delete operations can be safely applied across multiple different cloud regions or data centres, and no changes are lost in the event of a complete region or data-centre outage__

__SA Maintainer__: [Paul Done](mailto:paul.done@mongodb.com) <br/>
__Time to setup__: 45 mins <br/>
__Time to execute__: 30 mins <br/>


---
## Description

This proof shows how a database can lose changes if it does not provide the ability to guarantee that records are written to multiple cloud-regions or data-centres and then only be available to be queried when present in multiple regions/DCs, especially in the event a whole region/DC failure. The proof shows how MongoDB Atlas clusters, when configured with appropriate high availability preferences, can guarantee that records aren't lost in such circumstances when a whole region/DC fails.

For this proof, both types of application and database deployments, __local_aware__ (susceptible to record loss when a whole region/DC fails) and __global_aware__ (NOT susceptible to record loss when a whole region/DC fails) are proved using the same MongoDB Atlas cluster. A Python script is run to continuously writes records to MongoDB cluster's shard primaries and then attempts to read the same records back from the primary. When run in  _local\_aware_ mode, the script uses _WriteConcern=0_ and _ReadConcern=1_ settings for the application. This should result in errors being shown, when region/DC failover occurs, with some of the acknowledged written records shown to be lost, when trying to read them back. When run in  _global\_aware_ mode, the script uses _WriteConcern=Majority_ and _ReadConcern=Majority_ settings for the application, to guarantee _durability_ across regions/DCs. This should result in NO acknowledged written records being lost due to failover. The script logs any errors, for writes that can't subsequently be read, to a output log file, to enable you to determine whether data was lost, after the script has been run and terminated.

NOTE: The test Python script __MUST__ be run from an AWS instance, for this proof, rather than from your laptop, because if the network speed between the client and the the database's primaries is inferior to the network speed between different database replicas in each replica-set, there is a high likelihood that you will not be able to _trap_ in-flight writes during failure testing.


---
## Setup

__1. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* Create an __M30__ based 3 node replica-set with a __multi-cloud region deployment__, with a __100 GB of storage allocated__ per node (e.g. 100GB), with __backup disabled__ and with 1 replica deployed to __each of the following regions__ (you want to ensure large geographical distances between regions):
  * _Ireland (eu-west-1)_
  * _N.California (us-west-1)_
  * _Sydney (ap-southeast-2)_

![multi-region](img/multi-region.png "multi-region")

__2. Configure AWS Environment__
* Using your MongoDB 'Solution Architects' [AWS pre-existing account](https://wiki.corp.mongodb.com/display/DEVOPSP/How-To%3A+Access+AWS+Accounts), log on to the [AWS console](http://sa.aws.mongodb.com/) and near the top right hand side of the AWS Console, __change the region__ to __NOT__ be in the AWS regions as you the ones you deployed the multi-region Atlas cluster to (for example set the region to _London (eu-west-2)_ or _N. Virginia (us-east-1)_)
* Launch (create) a new EC2 instance with the following settings (use defaults settings for the rest of the fields):
  * __AMI Type__: Amazon Linux 2 AMI (HVM), SSD Volume Type
  * __Instance Type__: m5.large
  * __Add Tags__: Be sure to set the 3 specific tags ('Name', 'owner', 'expire-on') on your instance as per the [MongoDB AWS Usage Guidelines](https://wiki.corp.mongodb.com/display/DEVOPSP/AWS+Reaping+Policies) to avoid your instance from being prematurely reaped
  * __Security Group__: Create a new security group which has an inbound rule to allow SSH only on port 22 from source 0.0.0.0/0
* When prompted, choose to use your existing key pair or create a new key pair (typically named similar to 'firstname.lastname'). If creating a new key pair, be sure to click the button to __Download Key Pair__ and store the key somewhere safe on your laptop.
*  Once the AWS instance is running, find it in the AWS Console __instances__ list, select it, and in the description section near the bottom of the AWS Console locate the __IPv4 Public IP__ field and make a note of its value
* Now go to the __Atlas Console__ and in the Security tab, add a new __IP Whitelist__ entry for the IP address you just captured, to allow the AWS instance to connect to your Atlas cluster

__3. Configure The Safety Checker Python Client (that will perform Inserts & Finds)__
* In the AWS Console __instances__ list select your AWS instance, press the __Connect button__ and follow the instructions to SSH into this instance from a new terminal window on your laptop
* In this SSH terminal session, run the following commands to update the system and to install __Python3__:
  ```bash
  sudo yum -y update
  sudo yum -y install python3
  python3 --version
  ```
* In the SSH session, run the following commands to download and install the PIP Python package manager:
  ```bash
  curl -O https://bootstrap.pypa.io/get-pip.py
  python3 get-pip.py --user
  vi .bash_profile
     (change the PATH line to following to ensure '/.local/bin' is first on the path and then save [:wq]):
     PATH=$HOME/.local/bin:$HOME/bin:$PATH
  source .bash_profile
  ```
* In the SSH session, install the Python MongoDB Driver and DNS Library:
  ```bash
  pip3 install --user pymongo dnspython
  ```
* In a new terminal/shell on your laptop (i.e. NOT in the SSH session), from the root folder of this proof (the folder containing 'check-safety.py'), use Secure Copy (SCP) to copy the main Python script and the large dummy JSON sub-document to the AWS Instance (this JSON file will be used by the script, under the covers, to ensure _large_ documents are written to the database). For example run the following two file copy commands (first changing the _pem_ file path/name and target the _DNS name_ of the AWS instance to the same values you used to connect an SSH session to the AWS instance, earlier):
  ```bash
  scp -i "pathto/first.last.pem" check-safety.py ec2-user@ec2-35-176-224-150.eu-west-2.compute.amazonaws.com:~/
  scp -i "pathto/first.last.pem" large_subdoc.json ec2-user@ec2-35-176-224-150.eu-west-2.compute.amazonaws.com:~/
  ```
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Python version__  copy the __Connection String Only__ - make a note of this MongoDB URL address to be used later


    
---
## Execution

__TEST 1. Prove that some writes may be lost during a failover for 'local-aware' settings__
* From the AWS instance's SSH session, start up the Python script, which continuously performs writes and then reads of those written records using multiple parallel processes, with the __LOCAL-AWARE__ settings (change the URL to the SRV connection address copied earlier and specify the password you set earlier - include inside double quotes - exclude any url parameters related to _retyWrites=_ or _w=_:
  ```bash
  ./check-safety.py "mongodb+srv://main_user:MyPassword@testcluster-abcde.mongodb.net" LOCAL-AWARE
  ```

&nbsp;&nbsp;&nbsp;&nbsp;__Important:__ Do not include _retryWrites=true_ in the URL above otherwise the client will just try to perform the write operation again on the new 'failed over to' primary server, when we are testing to see that the original write didn't make it.
* In a separate SSH terminal session for the same AWS instance, continuously monitor the output of the scripts log file, to look for errors:
  ```bash
  tail -f consistency.log
  ```
* From the Atlas console, select the __.../Test Failover__ option to force a failure of the replica-set's primary server; the Atlas console will then show a dialog similar to the following:
![test-failover](img/test-failover.png "test-failover")
* For the next few minutes, keep watching the output of the two SSH terminal sessions (one running the Python script, one tailing the log file) and when these start to show extra warning or error messages this should indicate that failover is now occurring in the Atlas cluster. __Wait at least 1 minute__ because if the script detects it can't read its write then it will wait a minute before trying again, once it is confident that a new primary should have been elected. Then stop the Python script using __Ctrl-C__
* Check the output of the `consistency.log` file to see if it contains one or more lines beginning `ERROR: INSERTED DOCUMENT NEVER FOUND` which indicates that a record was written but subsequently lost when the primary fails over (if any 'ERROR' lines are shown before failover is induced, ignore these, even though these are a sign of lack of consistency generally with _local-aware_ settings they don't relate to consistency during failover specifically):
  ```bash
  grep ERROR consistency.log
  ```
The appearance of these __errors__ shows that with 'local-aware' settings for a database (in MongoDB's case, when WriteConcern is set to 0 and ReadConcern is set to 1), some recently acknowledged writes may be lost. __If no errors are detected, this could just be because there were no in-flight writing of records which had been persisted on a primary but not yet replicated__, at the time of failover occurring. If that is the case, __re-run__ the Atlas __Test Failover__ operation again to see if the errors are induced on a second attempt (you may need to run the test a few times because essentially you are testing for a potential _race conditions_).

__TEST 2. Prove that no writes are lost during a failover for 'global-aware' settings__
* Again, from the SSH session, start up the Python script which continuously performs writes and then reads of those written records using multiple parallel processes, __but this time__ with the __GLOBAL-AWARE__ settings (change the URL to the SRV connection address copied earlier and specify the password you set earlier):
  ```bash
  ./check-safety.py "mongodb+srv://main_user:MyPassword@testcluster-abcde.mongodb.net" GLOBAL-AWARE
  ```

&nbsp;&nbsp;&nbsp;&nbsp;__Important:__ Do not include _retryWrites=true_ in the URL above otherwise the client will just try to perform the write operation again on the new 'failed over to' primary server, when we are testing to see that the original write didn't make it.
* In a separate SSH terminal session for the same AWS instance, continuously monitor the output of the scripts log file, to look for errors:
  ```bash
  tail -f consistency.log
  ```
* From the Atlas console, select the __.../Test Failover__ option to force a failure of the replica-set primary server
* Again, for the next few minutes, keep watching the output of the two SSH terminal sessions (one running the Python script, one tailing the log file) and when these start to show extra warning or error messages __wait another 1 minute__ before stopping the Python script using __Ctrl-C__
* Check the output of the `consistency.log` file to see if it contains one or more lines beginning `ERROR: INSERTED DOCUMENT NEVER FOUND` which indicates that a record was written but subsequently lost when the primary fails over:
  ```bash
  grep ERROR consistency.log
  ```
For 'global-aware' mode __no errors should ever appear__ in the file, regardless of however many times the _test-failover_ Atlas function is re-run, because the deployment configuration (and underlying database technology) supports safe writes and reads across regions/DCs. Specifically, in MongoDB's case, both WriteConcern and ReadConcern are set to Majority to enable this.


---
## Measurement

For __Test 1__ (_prove that some writes may be lost during a failover for 'local-aware' settings_), __ERRORS__ should appear in the `consistency.log` file, after enough test runs, indicating that the deployment __CANNOT__ guarantee safe-writes across regions/DCs, similar to below (if any 'ERROR' lines are shown before failover is induced, ignore these, even though these are a sign of lack of consistency generally with _local-aware_ settings they don't relate to consistency during failover specifically):
  ```
  INFO: EXCEPTION TRYING TO DO FIND - 20:24:31 - process_id 6 - index 13159: connection closed
  INFO: DUE TO THE MISSED FIND WILL TRY AGAIN AFTER A DELAY TO ALLOW NEW PRIMARY TO COME UP - 20:24:31 - process_id 6 - index 13159
  INFO: EXCEPTION TRYING TO DO FIND - 20:24:31 - process_id 0 - index 16363: connection closed
  INFO: DUE TO THE MISSED FIND WILL TRY AGAIN AFTER A DELAY TO ALLOW NEW PRIMARY TO COME UP - 20:24:31 - process_id 0 - index 16363
  INFO: EXCEPTION TRYING TO DO FIND - 20:24:31 - process_id 4 - index 15771: connection closed
  INFO: DUE TO THE MISSED FIND WILL TRY AGAIN AFTER A DELAY TO ALLOW NEW PRIMARY TO COME UP - 20:24:31 - process_id 4 - index 15771
  ERROR: INSERTED DOCUMENT NEVER FOUND - 20:25:31 - process_id 4 - index 15771
  ERROR: INSERTED DOCUMENT NEVER FOUND - 20:25:31 - process_id 6 - index 13159
  ERROR: INSERTED DOCUMENT NEVER FOUND - 20:25:31 - process_id 0 - index 16363
  ```

For __Test 2__ (_prove that no writes are lost during a failover for 'global-aware' settings_), __NO ERRORS__ should ever appear in the `consistency.log` file, indicating that the deployment does guarantee safe-writes across regions/DCs, similar to below:
  ```
  INFO: EXCEPTION TRYING TO DO FIND - 20:31:28 - process_id 2 - index 311: connection closed
  INFO: DUE TO THE MISSED FIND WILL TRY AGAIN AFTER A DELAY TO ALLOW NEW PRIMARY TO COME UP - 20:31:28 - process_id 2 - index 311
  INFO: EXCEPTION TRYING TO DO FIND - 20:32:11 - process_id 0 - index 338: connection closed
  INFO: DUE TO THE MISSED FIND WILL TRY AGAIN AFTER A DELAY TO ALLOW NEW PRIMARY TO COME UP - 20:32:11 - process_id 0 - index 338
  INFO: EXCEPTION TRYING TO DO FIND - 20:32:11 - process_id 5 - index 339: connection closed
  INFO: DUE TO THE MISSED FIND WILL TRY AGAIN AFTER A DELAY TO ALLOW NEW PRIMARY TO COME UP - 20:32:11 - process_id 5 - index 339
  INFO: FOUND DOC ON SECOND TRY, AFTER A SLEEP - 20:32:28 - process_id 2 - index 311
  INFO: FOUND DOC ON SECOND TRY, AFTER A SLEEP - 20:33:11 - process_id 5 - index 339
  INFO: FOUND DOC ON SECOND TRY, AFTER A SLEEP - 20:33:11 - process_id 0 - index 338
  ```

