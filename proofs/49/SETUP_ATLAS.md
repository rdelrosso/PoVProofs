# Setup an Atlas Cluster

## Configure Atlas Environment

* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project

* Create an replica set __M0__ (or __M2__ or __M5__) tier deployment in a supported cloud provider and region - __Realm Sync requires MongoDB version 4.4__ and at the time of writing only the _US-EAST-1_ region on AWS was supported. Name the cluster __RealmCluster__ (this is required for the import of the Realm application - alternatively update the cluster name in the Realm config file.)

* Once the cluster has been fully provisioned, in the Atlas console, click the __... (*ellipsis*)__ for the cluster, select __Load Sample Dataset__ and in the modal dialog, confirm that you want to load the sample dataset by choosing __Load Sample Dataset__.

* From the Atlas console click the __Connect button__, select __Connect With MongoDB Compass__ and click the __Copy__ button to copy the connection string - make a note of this MongoDB URI address to be used later.
