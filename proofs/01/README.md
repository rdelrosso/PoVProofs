# RICH-QUERY

__Ability to run a single expressive and efficient query targeting a specific subset of records using compound criteria spanning a number of fields, including fields in sub-documents & array elements__

__SA Maintainer__: [Ronán Bohan](mailto:ronan@mongodb.com) <br/>
__Time to setup__: 30 mins <br/>
__Time to execute__: 15 mins <br/>

---
## Description

This proof shows how MongoDB can perform expressive queries using query criteria spanning a number of fields and how secondary indexes can be leveraged to greatly reduce query response time and minimise database overhead. Specifically, the proof will show that a collection of 1,000,000 randomly generated documents can be searched using a combination of elements, demonstrating the richness and flexibility of the query language. These elements will include:

* A date field
* A text field
* A boolean field
* A field that is in a sub document
* A field that is inside an array
* A range based filter

For the test 1,000,000 fictitious 'single view' insurance customer records are generated and loaded into a collection in a MongoDB Atlas cluster.

The expressive query that will be run will return all documents where the _"customer is Female, born in 1990, lives in Utah and has at least one Life insurance policy for which they are registered as a Smoker"_.


---
## Setup
__1. Configure Laptop__
* Ensure MongoDB version 3.6+ is installed on your laptop in order to access the MongoDB command line tools (a MongoDB Atlas cluster will be used to actually host the data)
* [Download](https://www.mongodb.com/download-center/compass) and install Compass on your laptop
* Ensure Node (version 6+) and NPM are installed your laptop
* Download and install the [mgeneratejs](https://www.npmjs.com/package/mgeneratejs) JSON generator tool on your laptop
  ```bash
  npm install -g mgeneratejs
  ```

__2. Configure Atlas Environment__
* __Note__: If using the Shared Demo Environment (https://docs.google.com/document/d/1cWyqMbJ_cQP3j7S4FJQhjRRiKq9WPfwPG6BmJL2bMvY/edit), please refer to the pre-existing collections for this PoV. (RICH-QUERY.customers & RICH-QUERY.customersIndexed)
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user, e.g. __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* Create an __M10__ based 3 node replica-set in a single cloud provider region of your choice with default settings
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Node.js version__ copy the __Connection String Only__ - make a note of this MongoDB URL address to be used in the next step

__3. Load Data Into A Collection In The Atlas Cluster__
* Generate 1,000,000 random JSON documents representing insurance customer 'single view' records, based on the `CustomerSingleView.json` template:

  ```bash
  mgeneratejs CustomerSingleView.json -n 1000000 | mongoimport --uri "mongodb+srv://main_user:mypassword@democluster-abcd.mongodb.net/RICH-QUERY" --collection customers --drop --numInsertionWorkers=10
  ```
Paste the copied URI into the `--uri` parameter, replacing the username & password fields with those you created earlier.
<br/><br/>
__Note__: This process generates over 1GB of data. The `mgeneratejs` process itself only takes ~10 minutes to complete but the upload process can take significantly longer if you're using a slow network connection.

__4. Check That The Collection's Data Can Be Accessed Using Compass__
* From the Atlas console click the __Connect button__, select __Connect With MongoDB Compass__ and click the __Copy__ button to copy the connection string
* Launch Compass and when prompted select to use the __MongoDB Connection String__ detected from the clipboard, fill in the __Username__ and __Password__ fields as required and then click the __Connect__ button
* In Compass, navigate to the __RICH-QUERY.customers__ collection and select the __Schema__ tab, press the __Analyze Schema__ button and ensure some result data is shown


---
## Execution

We will use Compass to find people in the database who:
 * are Female: `{ 'gender': 'Female' }`
 * were born in 1990: `{ 'dob': { '$gte': ISODate('1990-01-01'), '$lte' : ISODate('1990-12-31') }}`
 * live in Utah: `{ 'address.state': 'UT' }`
 * have at least one Life insurance policy for which they are registered as a Smoker: `{ 'policies': {'$elemMatch': { 'policyType': 'life', 'insured_person.smoking': true }}}`

__1. Run The Test Query As-Is__
* In the Compass __Documents__ tab, enter the following query filter:
  ```
  FILTER: { 'gender': 'Female', 'dob': { '$gte': ISODate('1990-01-01'), '$lte' : ISODate('1990-12-31')}, 'address.state': 'UT', 'policies': { $elemMatch: {'policyType': 'life', 'insured_person.smoking': true }}}
  ```
* Clicking the __FIND__ button returns the matching documents:
  ![query1](img/query1.png)
* Note the number of documents returned - 63 in this example. It's also important to highlight that the client application was not involved in processing the query - all the data was found and returned by the database engine.
* Switch to the __Explain
Plan__ tab and click the __Explain__ button.
![plan1](img/plan1.png)
* Note that this query performed a 'collection scan' (__COLLSCAN__) across all 1 million documents. In this particular example 1 million documents were examined and 63 documents were returned in 3844ms. Also note that no index was used to satisfy the query.

__2. Run The Test Query Again Returning Just The Data We Need__
* Back on the __Documents__ tab click the __OPTIONS__ button and update the projection field as follows:
  ```
  PROJECT: { '_id': 0, 'firstname': 1, 'lastname': 1, 'dob': 1 }
  ```
* Click the __FIND__ button and validate the set of returned documents only include the person's name and date of birth.
![query2](img/query2.png)
* Switch back to to the __Explain Plan__ tab and execute the __Explain Plan__ again.
![plan2](img/plan2.png)
* Note that the same number of documents are returned in approximately the same amount of time (3742ms). This time however, we see a new __PROJECTION__ stage which reduces the volume of data returned to the client, minimizing network bandwidth in the response.

__3. Create An Appropriate Index__

__NOTE:__ If running this using a pre-built Shared Demo Environment, skip this section 3 (don't try to create an index) because a separate copy of the collection (_RICH-QUERY.customersIndexed_) has been created for use in section 4.

* In the Compass __Indexes__ tab, click the __Create Index__ button and add a new compound index called __index1__ with the following elements:
  ```
  FIELD: address.state, TYPE: 1 (asc)
  FIELD: policies.policyType, TYPE: 1 (asc)
  FIELD: policies.insured_person.smoking, TYPE: 1 (asc)
  FIELD: gender, TYPE: 1 (asc)
  FIELD: dob, TYPE: 1 (asc)
  ```
 ![index](img/index3.png)
 Note: For those that want to create index via cli use `db.customers.createIndex({"address.state":1, "policies.policyType":1, "policies.insured_person.smoking":1, "gender":1, "dob":1})`
* Press the _Create_ button to apply the index (the index may take a few 10s of seconds to be created against the 1m records). This index is very efficient in that it has been defined using the most specific fields in our query listed first, with the range field at the end.

__4. Run The Test Query Leveraging The New Index__

__NOTE:__ If running this using a pre-built Shared Demo Environment, a separate copy of the collection (_RICH-QUERY.customersIndexed_) has been created for use in this section, which is already indexed, so run the below steps against this separate _customersIndexed_ collection.

* In the Compass __Documents__ tab, execute the same query again and verify the same set of documents are returned as before.
* In the Compass __Explain Plan__ tab, examine the latest plan by clicking the __EXPLAIN__ button again.
![plan4](img/plan4.png)
* Here we see an 'index scan' (`IXSCAN`) is taking place instead of the earlier 'collection scan' (`COLLSCAN`).
* We also see from the plan and the metrics that only 63 index items were examined, resulting in 63 documents being fetched before the projection took place. The net result is a more efficient query taking just 18ms in this example.

&nbsp;__NOTE__: In some situations a _Covered Query_ can be used to allow the database to return the results for the query leveraging just an index, without fetching the underlying documents. In this example though, it is not possible to use a covered query due to the fact that the query targets an array field (see [Covered Queries](https://docs.mongodb.com/manual/core/index-multikey/#covered-queries) which states: `Multikey indexes cannot cover queries over array field(s)`)


---
## Measurement

At the end of the execution process you should have recorded results from the Compass 'Explain Plan' tab similar to the following (the number of documents examined/returned may vary a little due to fact that the data was randomly generated):

Test | Returned Docs | # Docs Examined | # Docs Returned | Time taken (ms)
-----|---------------|-----------------|-----------------|----------------
Simple query | Full Docs | 1m | 63 | 3844
Projection | Projected Fields only | 1m | 63 | 3742
Indexed Query | Projected Fields only | 63 | 63 | 18
