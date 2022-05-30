# JOINS

__Ability to perform the join of related data sets, directly in the database, for faster analytics__

__SA Maintainer__: [Felix Reichenbach](mailto:felix@mongodb.com) <br/>
__Time to setup__: 60 mins <br/>
__Time to execute__: 15 mins <br/>


---
## Description

This proof shows the ability for the MongoDB query and aggregation language to efficiently deal with data models where data is kept in multiple collections and needs to be joined together. 

For this proof, two collections are used, representing two different entities, animal owners and their animals, where each owner record has a field which is an array of references to the IDs of the animals owned.


---
## Setup
__1. Configure Laptop__
* [Download](https://www.mongodb.com/download-center/compass) and install Compass on your laptop
* Ensure Node (version 6+) and NPM are installed your laptop
* Download and install the [mgeneratejs](https://www.npmjs.com/package/mgeneratejs) JSON generator tool on your laptop
  ```bash
  npm install -g mgeneratejs
  ```

__2. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* Create an __M10__ based 3 node replica-set in a single cloud provider region of your choice with default settings
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Node.js version__  copy the __Connection String Only__ - make a note of this MongoDB URL address to be used later


__3. Load Data Into A Collection In The Atlas Cluster__
* Generate partly templated, partly randomly generated JSON documents representing owners and their animals documents where each collection contains 1 million records (ensure you change the cluster address and password to match your own settings recorded earlier, in the 2 commands below):
  ```bash
  mgeneratejs owners.json -n 1000000 | mongoimport --uri "mongodb+srv://main_user:mypassword@testcluster-abcde.mongodb.net/zoo" --collection owner

  mgeneratejs animals.json -n 1000000 | mongoimport --uri "mongodb+srv://main_user:mypassword@testcluster-abcde.mongodb.net/zoo" --collection animals
  ```

 &nbsp;&nbsp;&nbsp; __Note__: The load process will take around 10 minutes to complete

__4. Check That The Collection's Data Can Be Accessed Using Compass__
* For the deployed database cluster, in the Atlas console, click the __Connect button__, select __Connect With MongoDB Compass__ and click the __Copy__ button to copy the connection string
* Launch Compass and when prompted select to use the __MongoDB Connection String__ detected from the clipboard, fill in the __Password__ field and then click the __Connect__ button
* In Compass, for the __zoo.owner__ and __zoo.animals__ collections, select the __Schema__ tab, press the __Analyze Schema__ button and ensure some result data is shown
    

---
## Execution

In Compass select the _owners_ collection and navigate to the __Aggregations__ tab to show the aggregation pipeline builder. Click the button __...__ then choose the __New Pipeline From Text__ and copy & paste the following pipeline into the dialog window...
```js
[
  {
    '$lookup': {
      'from': 'animals', 
      'localField': 'animals', 
      'foreignField': '_id', 
      'as': 'owns'
    }
  }
]
```

...then click __Create New__ button to create a pipeline that performs a join of the _owners_ collection to the _animals_ collection, as shown in the screenshot below: 

![AggPipeline_create](img/AggPipeline_create.png "Create Agg. Pipeline")

The subsequent aggregation results displayed in Compass should show a sample of the first 20 _owner_ documents where each _owner_ document embeds the list of her/his _animals_, with full animal details, in an array of sub-documents named _owns_

Optionally you could add a $unwind stage and create an individual document for each animal combined with its owner


---
## Measurement

The result of the executed aggregation visible in Compass should show each _Owner_ document with full details of the owner's animals joined in to the _owns_ field as an array of sub-documents, as shown in the screenshot below:

![AggPipeline_lookup](img/AggPipeline_lookup.png "$lookup")

