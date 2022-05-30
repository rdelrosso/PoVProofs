# How to show consistency failures ? [IN PROGRESS]

Due to the efficiency of MongoDB replication process, it can be tricky to find a way to fail consistency. Removing sessions, causal consistency and readConcern majority is not enough, you need to stress the opLog.

The following procedure should help:

* Install [POCDRIVER](https://github.com/johnlpage/POCDriver) in a cloud hosted VM in the same region as your ATLAS Cluster
* Run the updateAndCheckPeopleEventualConsistency.py script :
** 
* run POCDRIVER in stress mode, with a MongoDB user having readWriteAnyDatabase and clusterMonitor roles :
  ```bash
  ./java -jar POCDriver.jar -c "mongodb+srv://main_user:PASSWORD@testcluster-abcd.mongodb.net/test"
  ```
* run ```$ tail -f consistency.log | grep "CONSISTENCY ERROR"```, you should get some :

  ```CONSISTENCY ERROR - 11:21:18 - process 4 - index 6423 - loop 114 - wrote $age=31 read $age=49```

