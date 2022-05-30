# ARCHIVE-STORAGE

__Ability to still access data, archived from an online database to inexpensive public cloud-native object storage, and still access the data with the same query capabilities as the original database provided__

__SA Maintainer__: [Fuat Sungur](mailto:fuat.sungur@mongodb.com) <br/>
__Time to setup__: 45 mins <br/>
__Time to execute__: 15 mins <br/>

---
## Description

This proof shows how hot data from a MongoDB Atlas replica-set can be offloaded to an AWS S3 bucket and then be directly queried and aggregated by MQL from this bucket without needing to load this data back into in a MongoDB cluster. MongoDB Atlas Data Lake's serverless ability to read archived data is leveraged for this proof.

For this proof, an Atlas cluster will be loaded with [sample data](https://docs.atlas.mongodb.com/sample-data/) and  **theaters** collection in the **sample_mflix** database will be copied to an S3 bucket to show that it can still be queried using MQL, via Atlas Data Lake.

In this proof, for an SA to use the Data Lake service __a preexisting Atlas project, AWS bucket and AWS IAM role must be leveraged__. See this [help document](https://docs.google.com/document/d/1XGz_VLTIjdZcbk9-Zp2ARkZEhx7ZopHn2xKkAEno770/) for details on the SA regional team's projects & buckets for EMEA. Each SA is already allocated to a preexisting _Atlas Organisation_ (e.g. _SA Team South Europe_), which contains a dedicated _Atlas Project_ called __Atlas Data Lake__. This project is shared by all the SAs in the region and contains an already configured _Data Lake_ service pointing at an existing shared AWS SA bucket for your SA region. Therefore in this proof, __you will NOT be configuring a new _Data Lake_ service__ and instead, you will be using an existing Data Lake service which some of your colleagues will also be using. Hence some care has to be taken not to override each other's settings - appropriate warnings for this are given below.

---
## Setup

**1. Configure Laptop**

- Ensure MongoDB Shell version 4.0+ is already installed on your laptop or the client machine.

**2. Check Existing Atlas Data Lake service**

- In the Atlas console, in the top-level __Context dropdown__ select your [SA region](https://docs.google.com/document/d/1XGz_VLTIjdZcbk9-Zp2ARkZEhx7ZopHn2xKkAEno770/) project called __Atlas Data Lake__ and once the project is open, select __Data Lake__ from the left menu, and you will be presented with the summary of a preexisting Data Lake service

![datalake](img/datalake_01.png)
![datalake](img/datalake_02.png)



If you are unable to see the project **Atlas Datalake** in your organization, please ask your organization owner to create an Atlas Data Lake for your organization. We will not cover the creation of Atlas Data Lake in this PoV.

**3. Configure AWS S3 Environment**

As of today, Data Lake is only supported on AWS S3 Bucket.

- Using your MongoDB 'Solution Architects' [AWS pre-existing account](https://wiki.corp.mongodb.com/display/DEVOPSP/How-To%3A+Access+AWS+Accounts), log on to the [AWS console](http://sa.aws.mongodb.com/).
- Select **S3** Service in AWS and search for the bucket in your region, e.g. **semeabucket** for _SA Team South Europe_ SAs (see [list](https://docs.google.com/document/d/1XGz_VLTIjdZcbk9-Zp2ARkZEhx7ZopHn2xKkAEno770/edit#) of the other SA regional team's buckets for EMEA) 
- In the AWS S3 Console, inside your bucket, click the __+ Create Folder__ button and name the new folder _firstname.lastname_ to match your name. The reason we choose *firstname.lastname* is not to have the same folder with any other SA in your region 
- The created folder in the S3 bucket may look like as below:
![s3_created_folder](img/s3_created_folder.png)
- Later to load data to S3 you will need your AWS __ACCESS\_KEY__ (_Access key ID_) and __SECRET\_KEY__ (_Secret access key_). If you don't know/remember your AWS KEYS you can re-generate through MANA


**4. Configure Atlas Replica Set**

The reason why we have a running Atlas database in this POV is to get an export the entire collection and load it into the S3 bucket.

- Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
- In the project's Security tab, choose to add a new user called **main_user**, and for **User Privileges** specify **Read and Write to any Database** (make a note of the password you specify)
- Also in the project's Security tab, add a new **IP Whitelist** and select to **Use Current IP Address** to ensure the Mongo Shell, which will run on your laptop later, will be allowed to connect to the cluster. If you use an EC2 instance as client, you should add the external IP address of the EC2 instance
- Create an **M10** based 3 node replica-set in a single AWS region of your choice with default storage settings
* Once the cluster has been fully provisioned, in the Atlas console, click the **... (*ellipsis*)** for the cluster, select **Load Sample Dataset**. In the modal dialog, confirm that you want to load the sample dataset by choosing **Load Sample Dataset**
- In the Atlas console, for the database cluster you deployed, click the **Connect button** , select **Connect with the Mongo Shell**, and in the **Run your connection string in your command line** section copy the connection command line - make a note of this connection command line to be used later

**5. Configure Python Environment**

You can execute the Python script for loading data from the Atlas MongoDB cluster to an AWS S3 bucket by using either

- Your laptop 

  OR

- Using an AWS EC2 VM instance (t2.micro would be fine as instance type)



**Client Dependencies**

- Python3, PIP3, PyMongo, AWS's Python client API library (Boto3) and some other Python dependencies are required. The list below shows what dependencies need to be installed on the client, and also if the client is an EC2 instance running Amazon Linux 2, the exact commands to run to pull in these dependencies are shown.

- __Install Python3__ - For EC2, in an SSH terminal session connected to your EC2 instance, run the following commands to update the system and to install Python3:
  ```bash
  sudo yum -y update
  sudo yum -y install python3
  python3 --version
  ```
- __Install & Configure PIP3__ - For EC2, in the SSH session, run the following commands to download and install the PIP Python package manager:
  ```bash
  curl -O https://bootstrap.pypa.io/get-pip.py
  python3 get-pip.py --user
  vi .bash_profile
     (change the PATH line to following to ensure '/.local/bin' is first on the path and then save [:wq]):
     PATH=$HOME/.local/bin:$HOME/bin:$PATH
  source .bash_profile
  ```
- __Install PyMongo, DNSPython & Boto3 Libraries__ - For EC2, in the SSH session, install the Python MongoDB Driver and other required Python Library:
  ```bash
  pip3 install --user pymongo dnspython boto3
  ```

---
## Execution

**1.** Ready to export movie _theaters_ collection from MongoDB Atlas, launch a command line terminal on your client and from the base director of this specific proof, in preparation for running the [mongo-to-s3-loader.py](mongo-to-s3-loader.py) python script which will copy the contents of the sample _theaters_ collection from the Atlas cluster to an AWS S3 Bucket.

**2.** Using a text editor first open up and edit the [mongo-to-s3-loader.py](mongo-to-s3-loader.py) changing the values for the following variables to match your environment: 
- __AWS_ACCESS_KEY__
- __AWS_SECRET_KEY__
- _urlAtlas_ (both __PASSWORD__ & __CLUSTERID__ you created before)
- __bucket__ (where you want to import, e.g. cemeabucket)
- __unique_folder__ (folder in S3 bucket, which you created before, e.g. firstname.lastname)

After the configure variables in the mongo-to-s3-loader.py, variables should look like below:


```python
AWS_ACCESS_KEY = 'myaccesskey'
AWS_SECRET_KEY = 'mysecretkeynobodyknows'
urlAtlas = 'mongodb+srv://main_user:password123@cluster1.5tka5.mongodb.net/test?retryWrites=true&w=majority'
bucket = 'semeabucket'
unique_folder = 'fuat.sungur' 
```

**3.** Now run Python script from the command line terminal:

  ```bash
  ./mongo-to-s3-loader.py
  ```

Output should look like this:

```bash
$ ./mongo-to-s3-loader.py
Connect to Atlas Cluster...
Download data into file...
Upload data to S3 bucket...
done
```

**4.** Go back to the AWS S3 console, navigate into your folder, hit browser refresh and then check that a sub-folder now exists which is the name of the _theaters_ collection and within that sub-folder there is some gzipped JSON data - this is the data exported from Atlas into the S3 bucket. The file path will be similar to `mybucket/first.last/theaters/theaters.json.gz`  (if you want to, you can select the gzip file in the AWS S3 Console and quickly use the __Select from__ capability to peak inside the file and view some of the JSON it contains)

![datalake](img/s3_exported_collection_zip.png)

**4.** Go back to the MonogDB Atlas console, select _Data Lake_ form the left hand menu and then copy the _Mongo Shell_ connection string![connect](img/connectADL.png) 

You should also add your current IP Address in the IP Whitelist for the Atlas Data Lake as shown in the below.

![connect](img/ip_whitelist.png)

**5.** From the terminal launch the Mongo Shell with the connection string to connect to the Data Lake cluster (replace __\<password\>__ in the connection string with the password listed in the [SA regional help document](https://docs.google.com/document/d/1XGz_VLTIjdZcbk9-Zp2ARkZEhx7ZopHn2xKkAEno770/) (e.g. 'M0ng0DB')

**6.**
In the Mongo Shell run following command to save a configuration in a temporary variable.

```bash
conf = db.runCommand("storageGetConfig")
```

**7.**
**Store**: The Store defines which S3 bucket is used for the connected Atlas Data Lake.

Check the existing stores for the connected Atlas Data Lake.

```bash
conf.storage.stores
```

It may return the store information shown in the below:
```bash
> conf.storage.stores
[
	{
		"name" : "semeabucket",
		"provider" : "s3",
		"region" : "us-east-2",
		"bucket" : "semeabucket",
		"delimiter" : "/"
	}
]
```
If you see the result then it shows that a STORE has already been defined for the connected Atlas Data Lake.

A Store in Atlas Data Lake, has an arbitrary name and a bucket name. In the above example, the arbitrary name is *semeabucket* and linked S3 Bucket is *semeabucket* -- this is the bucket name in AWS S3.

**If we cannot see already defined STORE**, we can create a STORE and link this store with the S3 Bucket.

```bash
conf.storage.stores.push({"s3" : {"name" : "my-semea-store", "region" : "eu-west-2", "bucket" : "semeabucket", "delimiter" : "/", "prefix" : "/"}})
```
Here, store name is *my-semea-store* and bucket is *semeabucket*. We'll use store name later while we are defining the databases for Atlas Data Lake.

**7.**

After we accessed/created the store in our Data Lake, then we can create a new database by mapping this database to a Store in our Data Lake.

You can check the existing databases in the Data Lake by issuing the following in the MongoDB Shell:

```bash
conf.storage.databases
```

It will print out the existing databases with the mapped Stores.

We will add one more database to our data lake. While adding the new database we should specify the store name as parameter.

The following example creates a database in our Atlas Data Lake with the name ```fuat-sungur``` and assigns the collection ```theaters``` to this database. The data of the ```theaters``` collection is all files under the  ```/fuat.sungur/theaters``` folder in the bucket ```semeabucket``` in S3. 

Before executing the below command, you should change:

- ```name``` field with the proper unique database name. Since "." (dot) is not allowed in the database name, we used a hyphen. 
- ```storeName``` field with the store name which you have already identified/created in Step 6
- ```path``` field with the relative folder in the S3 Bucket

```bash
conf.storage.databases.push({
    "name" : "fuat-sungur",
    "collections" : [
        {
            "name" : "theaters",
            "dataSources" : [
                {
                    "storeName": "semeabucket",
                    "path" : "/fuat.sungur/theaters/*"
                }
            ]
        }
    ]
})
```

After you issue the command, Mongo Shell will print out the total number of databases in the store.

Please see the [Atlas Data Lake Documentation](https://docs.atlas.mongodb.com/reference/data-lake-configuration/#stores) for further details

**8.**

After you've successfully added the new database to the ```conf``` variable then you need to reconfigure Atlas Data Lake. Otherwise,

```bash
db.runCommand({"storageSetConfig": conf.storage})
```

After the execution you should be able to see the below response:
```bash
{ "ok" : 1 }
```

Furthermore, even you can check the Configuration of Data Lake in the Atlas UI Console. 
Go To Atlas UI Console. Click **"Data Lake"** in the left sidebar menu. Then Click the **"Configuration"** button at the top right of the Data Lake Service. Then you will see the configuration of the Data Lake (store and databases information) as shown below.

![datalake](img/atlas_data_lake_configuration.png)

Come back to Mongo Shell which you connected to the Atlas Data Lake.


Check if your new created database and collection is now available (replace _firstname-lastname_ below with your DB name):

```bash
show dbs
use firstname-lastname
show collections
db.theaters.find().limit(2)
```

---
## Measurement

**1.**
Run the following simple MQL query below (replace _first-last_ below with your DB name) from 2 different Mongo Shells, one against your Atlas cluster and one against your Atlas Data Lake service and validate that they both display the same data to prove that the same MQL query can be run against matching data in an Atlas MongoDB database and in a Atlas Data Lake service and return the same results.

```bash
use firstname-lastname
db.theaters.find({theaterId: 8095}).pretty()
```

![mql_1](img/mql_1.png)

**2.**
Run an aggregation query from both Shells (one connected to the Atlas cluster and one connected to the Atlas Data Lake service) and again validate that they return the same results - the aggregation finds the top 5 cities that have the most theaters in US:

```
[{$group: {
  _id: "$location.address.city",
  ids: {
    $addToSet: "$theaterId"
  }
}}, {$addFields: {
  size: {$size: "$ids"}
}}, {$sort: {
  size: -1
}}, {$limit: 5}]
```

```
db.theaters.aggregate([{$group: {   _id: "$location.address.city",   ids: {     $addToSet: "$theaterId"   } }}, {$addFields: {   size: {$size: "$ids"} }}, {$sort: {   size: -1 }}, {$limit: 5}]).pretty()
```

![aggregation](img/aggr.png)

Both queries should show the same results with _Las Vegas_ having the most theaters.
