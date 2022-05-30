# Confluent Cloud

__Text describing something__

__SA Maintainer__: [Philipp Waffler](mailto:philipp.waffler@mongodb.com) <br/>
__Time to setup__: 60 mins <br/>
__Time to execute__: 15 mins <br/>

---
## Description
This proof shows that data from console game matches can be sourced from an Atlas Cluster to a Confluent Cloud Kafka Cluster via the MongoDB Atlas Source Connector (installed on a Kafka Connect Cluster on Confluent Cloud). In this process, we apply a filter pipeline to the changestreams used by the MongoDB Atlas Source Connector. This proof also demonstrates how data from the console game match, can be sunk into an Atlas Cluster, containing player profile data obtained from a Confluent Cloud Kafka Cluster, via the MongoDB Atlas Sink Connector. The following slide showcases the architecture.

<img src="screenshots/Screenshot%202022-01-05%20at%2010.54.41.png" width="1000">


The **setup of this proof** includes the following section:

1. [Configure your Laptop](#-configure-your-laptop)
2. [Configure your Atlas Environment](#-configure-atlas-environment)
3. [Import Player Profile Data](#-import-player-profile-data)
4. [Configure Confluent Cloud Environment](#-configure-confluent-cloud-environment)
5. [Set up MongoDB Atlas Source Connector](#-set-up-mongoDB-atlas-source-connector)
6. [Start Data Generation Script](#-start-data-generation-script)
7. [Set up MongoDB Atlas Sink Connector](#-set-up-mongoDB-atlas-sink-connector)
8. [Set up Atlas Trigger](#-set-up-atlas-trigger)

The **execution of this proof** is performed as follows: [CLICK](README.md#execution)

---
## Setup

## ![1](images/1b.png) Configure your Laptop
* Ensure __Python 3__ is installed and install required Python libraries:
  ```bash
  pip3 install pymongo dnspython
  ```
* Ensure __MongoDB Compass__ is installed. Here is a [link to the download](https://www.mongodb.com/try/download/compass) page.
* Ensure __MongoDB Database Tools__ are installed. Here is a [link to the installation](https://docs.mongodb.com/database-tools/installation/installation-macos/) guide.

## ![2](images/2b.png) Configure your Atlas Environment
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __admin__ with full priviledges.
* Create an __M10__ based 3 node replica-set on AWS. Name it _"PlayerCluster"_
* Create an __M0__ based 3 node replica-set on AWS in . Name it _"MatchCluster"_
* In the Security tab, add a new __IP Whitelist__ for all IP addresses (0.0.0.0/0).
* In the Atlas console, for the database clusters you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Python version__  copy the __Connection String Only__ - make a note of these MongoDB URL addresses to be used later.

## ![3](images/3b.png) Import Player Profile Data
* Download the files containing the [players' profile data](game_clean)
* Use _mongorestore_ to load this data into your _"PlayerCluster"_. Therefore navigate in your shell (e.g. iTerm) to the directory where you placed the directory  _game_clean_ and execute the following command:

  ```bash
  mongorestore --uri "mongodb+srv://playercluster.l5iko.mongodb.net/sample_kafka" --username admin --password *********** game_clean/
  ```
* _(optional)_ Check e.g. in MongoDB Compass if the data has arrived.

## ![4](images/4b.png) Configure Confluent Cloud Environment

Here you will setup a Confluent Cloud account (if you do not already have one) and subsequently create a Kafka Cluster _without_ any connectors in it. The setup of the connectors is part of a later step.

__Set up your Account__
* Navigate to the [Confluent Cloud](https://confluent.cloud) website and set up a free account.
* Confluent Cloud does not offer a forever free tier cluster (like M0 in MongoDB Atlas). Instead they offer **$400 ** in **Free Credits**. Check your Free Credits by navigating to the **Billing & payment** section. <br/><br/>
  <img src="screenshots/Screenshot%202022-01-05%20at%2009.23.25.png" width="700">
* Feel free to add the promo code ```C50INTEG``` for extra $50 of free credits.
* **Attention:** In order to incur no ongoing charges, always delete your Kafka Connectors on Confluent Cloud. In this POV, the deletion process **is** already included and described below. If you feel like experimenting yourself, keep the deletion process in mind.

__Create a Cluster__
* Create your Kafka Cluster by choosing _"Basic"_ as cluster type. The cluster itself is for free, yet installed connectors will incur charges towards your free credits. <br/><br/>
  <img src="screenshots/Screenshot%202021-11-23%20at%2014.48.52.png" width="700">
* Choose the same AWS region for your Confluent Cloud Kafka Cluster as you installed your Atlas Cluster in. <br/><br/>
  <img src="screenshots/Screenshot%202021-11-23%20at%2014.49.46.png" width="700">
* At this point you will have to set up your payment method. $400 is enough to execute this POV about 20-40 times. 
* Once you finished the setup, navigate to your new cluster and make yourself familiar with the GUI of Confluent Cloud.
* As a last step, navigate to _Data Integration/Connectors_, where we will set up the MongoDB Atlas Source and Sink Connector. <br/><br/>
  <img src="screenshots/Screenshot%202021-11-23%20at%2014.54.59.png" width="500">

## ![5](images/5b.png) Set up MongoDB Atlas Source Connector
* Select the MongoDB Atlas Source Connector and start filling out the fields
* **Kafka Cluster credentials**
  * **Kafka Cluster Authentication Mode**: KAFKA_API_KEY 
  * **Kafka API Key**: Generate an API key and write the credentials down in a safe place
  * **Kafka API Secret**: Use the previously generated API Secret
* **How do you want to name your topic(s)?**
  * **Topic prefix**: _match_
  * Other fields: empty
* **How should we connect to your MongoDB Atlas database?**
  * **Connection host**: Your Atlas connection string in the following format of your M0 _MatchCluster_: _"matchcluster.l5nko.mongodb.net"_
  * **Connection user**: Your Atlas user that you created for your M0 cluster, e.g. _admin_.
  * **Connection password**: Analogously to the _Connection user_. 
  * **Database name**: _sample_kafka_
* **Database details**
  * **Collection name**: _matches_
* **Connection details**
  * **Poll wait time (ms)**: _1000ms_ (We are inpatient)
  * **Maximum documents to include in a batch**: _12_ (As this is the maximum amount of documents we will insert with the provided script at a time)
  * **Pipeline**: ```[{"$match": { "fullDocument.matchCompleted": true}}]``` (We do not want to store unfinished matches in the player cluster - players that leave before the end should be penalized and receive no gold and XP)
  * Other fields: empty
* **Output messages**
  * **Output Kafka record format**: _JSON_
  * Other fields: empty
* **Number of tasks for this connector**
  * **Tasks**: _1_ (Since everything else would be overkill and no longer possible free tier cluster)  
* No Transforms or Predicates

Once the MongoDB Atlas Source Connector is set up, click on _NEXT_ and _LAUNCH_. Provisioning should take about 3-5 min. Once everything is set up successfully, you should see the new connector _Running_ in your Connector overview.

<img src="screenshots/Screenshot%202022-01-05%20at%2011.57.34.png" width="1000">

## ![6](images/6b.png) Start Data Generation Script
* Download the [inserter script](inserter.py)
* In **line 6**, add your own connection string for the M10 _"PlayerCluster"_.
* In **line 11**, add your own connection string for the M0 _"MatchCluster"_. Save the adjusted _inserter.py_.
* Execute the script via the shell. Therefore, navigate to the folder where you placed the _inserter.py_ and execute the following command in the sell:
  ```bash
  python3 inserter.py
  ```
* Visit your **Confluent Cluster** again and check out the data that is stored in topics. A new topic should be created by now that contains the messages sourced by the connector to Kafka. You should see data of the following form:

  <img src="screenshots/Screenshot%202022-01-05%20at%2011.56.37.png" width="1000">
  
* The `_id` field generated for the messages arriving in the Kafka topic is the resume token of the changestreams used by the MongoDB Atlas Source Connector. We will change this back to the original `_id` field when sinking the documents back into the _PlayerCluster_.
* _Offset_ represents the order in which messages arrived. You can get familiar with your messages and navigate through your topic by utilizing the _Offset_. Further detail can be found in the documentation of the [Message Browser](https://docs.confluent.io/cloud/current/client-apps/topics/messages.html).
* Your M0 cluster should now start receiving data from matches. You can check this e.g. in the Atlas GUI or in MongoDB Compass (e.g. as follows).<br/><br/>
  <img src="screenshots/Screenshot%202022-01-05%20at%2012.53.47.png" width="1000">
 
## ![7](images/7b.png) Set up MongoDB Atlas Sink Connector
Since our data is now already arriving in the Confluent Cloud Kafka Cluster, it is time to write it to MongoDB Atlas via the Sink Connector. We will use [SMTs (Single Message Transforms)](https://docs.confluent.io/platform/current/connect/transforms/overview.html) in order to transform the messages in a suitable way. 

* Select the MongoDB Atlas Sink Connector and start filling out the fields
* **Which topics do you want to get data from?**
  * **topics**: _match.sample_kafka.matches_ (hit ENTER do log in this topic)
* **Kafka Cluster credentials**
  * **Kafka Cluster Authentication Mode**: KAFKA_API_KEY 
  * **Kafka API Key**: Use the previously generated API Key from the steps outlined in the _Source Connector_. 
  * **Kafka API Secret**: Use the previously generated API Secret 
* **How should we connect to your MongoDB Atlas database?**
  * **Connection host**: Your Atlas connection string in the following format of your M10 _PlayerCluster_: _"playercluster.l5nko.mongodb.net"_
  * **Connection user**: Your Atlas user that you created for your M10 cluster, e.g. _admin_.
  * **Connection password**: Analogously to the _Connection user_. 
  * **Database name**: _sample_kafka_
* **Database details**
  * **Collection name**: _playerMatchesRaw_
* **Connection details**
  * All Fields: Empty
* **Time Series configuration**
  * All Fields: Empty
* **Number of tasks for this connector**
  * **Tasks**: _1_ 
* **Transform 1**
  * Type _renameAndRemove_ and click _Add Transform_
  * **Transformation type for renameAndRemove**: `org.apache.kafka.connect.transform.ReplaceField$Value`
  * **exclude**: `_ns` (ENTER) `documentKey` (ENTER) `operationType` (ENTER) (These fields from the Kafka topic will not be written to the _PlayerCluster_)
  * **renames**: `fullDocument._id:_id` (ENTER) `_id:resumeToken` (ENTER) (Renaming the _id field)
  * **Reasons and explanation behind this renaming**:
    * "_id" becomes "resumeToken", as the Kafka Source Connector has embedded the source document unter the "fullDocument" field and given the messages in the Kafka Cluster the "_id" of the change stream resume token (obtained by the change stream utilized by the Atlas Source Connector)
    * "fullDocument._id" becomes the new "_id" field, as we want to keep the original "_id" from the MatchCluster source documents
  
  * All other fields: Empty
  
  The final result of this transform should look as follows: <br/><br/>
  <img src="screenshots/Screenshot%202022-01-05%20at%2012.41.35.png" width="500">

* **Transform 2**
  * Type _convertTimestamp_ and click _Add Transform_
  * **Transformation type for convertTimestamp**: `org.apache.kafka.connect.transform.TimestampConverter$Value`
  * **target.type**: `Timestamp`
  * **field**: `clusterTime`
  * **format**: `yyyy-MM-dd HH:mm:ss`
* Predicates: Empty

In case the customer asks you what these transforms are - i.e. what [SMTs (Single Message Transforms)](https://docs.confluent.io/platform/current/connect/transforms/overview.html) are - or you are wondering out of curiosity:
* SMTs transform inbound messages after a source connector has produced them, but before they are written to Kafka. 
* SMTs transform outbound messages before they are sent to a sink connector. <br/><br/>
So in a sense they are transformations you can plug into the Kafka Source or Sink connector and they will transform the messages before they are written to Kafka or MongoDB Atlas respectively.

Once the MongoDB Atlas Source Connector is set up, click on _NEXT_ and _LAUNCH_. Provisioning should take about 3-5 min. Once everything is set up successfully, you should see the new connector _Running_ in your Connector overview.

<img src="screenshots/Screenshot%202022-01-05%20at%2012.04.15.png" width="1000">

The data arriving in MongoDB Atlas in the _PlayerCluster_ should have the following form:<br/><br/>
<img src="screenshots/Screenshot%202022-01-05%20at%2012.53.25.png" width="1000">

In the last step of the setup we configure an Atlas Trigger to convert the raw data accordingly.

## ![8](images/8b.png) Set up Atlas Trigger

To do so we log into MongoDB Atlas and choose Triggers on the left side and click Add Trigger on the new loaded page. Alternatively you may download the Realm App (in this GitHub Repo) and [set up the trigger via the CLI](https://docs.mongodb.com/realm/manage-apps/configure/copy-realm-app/). Setting this simple trigger up manually should be significantly faster and educational for most Solution Architects.

Following the manual setup, these are the steps:

* First, link the _PlayerCluster_ as a Data Source. If the Cluster is "greyed out", it is already linked as a data source.
* **Trigger Type**: Database
* **Name**: Choose an appropriate name, e.g. matchModTrigger
* **Enabled**: ON
* Choose your **Cluster** and the **database** and the **collection** _(e.g. PlayerCluster, sample_kafka, playerMatchesRaw)_
* **Operation Type**: Insert
* **Full Document**: ON
* **Document Preimage**: OFF
* **Event Type**: Function

Add the following function that should be executed, ones the Atlas Trigger is triggered.

``` javascript
exports = function(changeEvent) {
  const fullDocument = changeEvent.fullDocument;
  
  const mongodb = context.services.get('PlayerCluster');
  const db = mongodb.db('sample_kafka');
  const collection_mod = db.collection('playerMatchesModified');
  
  const modifiedDocument = {
    "_id": fullDocument._id,
    "geo": fullDocument.fullDocument.geoLocale.substring(0, 2),
    "locale": fullDocument.fullDocument.geoLocale.substring(3, fullDocument.fullDocument.geoLocale.length),
    "totalMatchTimeSeconds": fullDocument.fullDocument.totalMatchTimeSeconds,
    "mvpWin": fullDocument.fullDocument.mvpWin,
    "matchDataGained": fullDocument.fullDocument.matchDataGained,
    "playerId": fullDocument.fullDocument.playerId
    };
  
  collection_mod.insertOne(modifiedDocument)
    .then(result => {console.log(`Successfully inserted item with _id: ${result.insertedId}`); return result})
    .catch(err => {console.error(`Failed to insert item: ${err}`); return err});
};
```

The final resulting data should look as follows:

<img src="screenshots/Screenshot%202022-01-05%20at%2016.11.39.png" width="1000">

**WARNING**: DO not forget to delete your Connectors after you finished the POV. The cluster itself will not incur any cost, the connectors will (and if you forget them for a month or two, your free credits will be depleted). 

---
## Execution
After the setup, below are recommended steps that demonstrate the value of our Kafka Connectors. 

* **Preparation**: Pause the data generation script started in the setup. Delete the _playerMatchesRaw_ and _playerMatchesModified_ collections. 
* **Explain** the architecture. Use the diagram provided. 
* **Start** the data generation script. Show the data arriving in MongoDB by looking into the M0 _MatchCluster_ in compass.
* **Walk through** the settings of the Kafka Source Connector. Stress the importance of the _pipeline_ field.
* **Show** messages arriving in the corresponding Kafka topics.
* **Walk through** the settings of the Kafka Sink Connector. Stress the importance of the SMTs. Many transformations can already be covered here.
* **Show** the raw data arriving in MongoDB in your M10 _PlayerCluster_ in the _playerMatchRaw_ collection. Explain the _resumeToken_ (artifact from MongoDB change streams) and the _timestamp_ field (the timestamp at which data loaded into the Kafka cluster).
* **Walkthrough** the Atlas Trigger. Explain the "string dissection" and Atlas Triggers in general as part of an event-based architecture.
* **Show** the final data arriving in the _playerMatchModified_ collection.

The following aggregation pipeline provides and easy way to demonstrate that ALL the data that we wanted to source (_"matchCompleted: true"_) arrives in the _PlayerCluster_:
```
[{$match: {
 matchCompleted: true,
 mvpWin: true
}}, {$count: 'count'}]
```
Execute this aggregation pipeline on the _MatchCluster_ AND the _PlayerCluster_. Do not forget to remove _"matchCompleted: true"_ in case of the _PlayerCluster_, as this field is omitted by the Atlas Trigger.

**WARNING 1**: Make sure both to remove all remenants of your setup when your start the demonstration of this POV, as otherwise the above counts might not match.

**WARNING 2**: Do not forget to delete your Connectors after finishing the POV. The cluster itself will not incur any cost; the connectors will (if you ignore them for a month or two, your free credits will deplete).


