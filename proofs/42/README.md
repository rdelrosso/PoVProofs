# INCREMENTAL-ANALYTICS

__Ability to maintain a materialized view of the latest version of summary data, derived by continuosly performing incremental analytics in the background against the original raw data__

__SA Maintainer__: [Charlie Little](mailto:charlie.little@mongodb.com) <br/>
__Time to setup__: 30 mins <br/>
__Time to execute__: 15 mins <br/>

---
## Description

This proof shows how a [Materialized View](https://en.wikipedia.org/wiki/Materialized_view) can be maintained by leveraging MongoDB's ability to performs incremental analytics using its query, projection, and merge operators. A Materialized View (MV) is type of collection view used to improve performance of often-queried data by pre-executing the query and storing the results, incrementally, either whenever the source data is added/changed or on a periodic basis.  An MV can have its own indexes and have separate access control rules defined for it, with respect to the the source collection(s), providing flexibility in the access patterns supported by the view.

This proof uses the _sales_ collection from the [Atlas sample datasets](https://docs.atlas.mongodb.com/sample-data/available-sample-datasets/) [_sample_supplies_](https://docs.atlas.mongodb.com/sample-data/sample-supplies/#sample-supplies) database. A sample document from that collections looks as follows:

```javascript
{
	"_id" : ObjectId("5bd761dcae323e45a93ccfe8"),
	"saleDate" : ISODate("2015-03-23T21:06:49.506Z"),
	"items" : [
		{
			"name" : "printer paper",
			"tags" : [
				"office",
				"stationary"
			],
			"price" : NumberDecimal("40.01"),
			"quantity" : 2
		},
		{
			"name" : "notepad",
			"tags" : [
				"office",
				"writing",
				"school"
			],
			"price" : NumberDecimal("35.29"),
			"quantity" : 2
		}
	],
	"storeLocation" : "Denver",
	"customer" : {
		"gender" : "M",
		"age" : 42,
		"email" : "cauho@witwuta.sv",
		"satisfaction" : 4
	},
	"couponUsed" : true,
	"purchaseMethod" : "Online"
}
```

 A MongoDB shell script, [generate-sales.js](generate-sales.js), is used to update the _sales_ collection. The script simulates daily sales by adding randomly generated sales records, beginning on January 1st, 2018 and continuing daily while the script is run.
  
 A scheduled Atlas trigger runs a Stitch function, [report-generator.js](report-generator.js), once a minute to generate or update a _report_ collection (the materialized view) with aggregated data from the _sales_ collection. The trigger function uses an aggregation pipeline to generate the results and leverages the [$merge](https://docs.mongodb.com/manual/reference/operator/aggregation/merge/) pipeline operator to combine the results with the existing documents in the _report_ collection.

You can also update the report manually, by running the [report-generator.js](report-generator.js) function interactively. A more sophisticated implementation (not part of this proof), could go a step further by using MongoDB Changes Streams / Atlas Database Triggers to listen for new data arriving in the source collection and then immediately perform the incremental analytic operation using the new data, rather than running the incremental analytics process periodically.

---
## Setup

__1. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* Create an __M10__ based 3 node replica-set in a single cloud provider region of your choice and __IMPORTANTLY__ specify the MongoDB __version as 4.2__
* In the Atlas console, for the database cluster you deployed, click the __Connect__ button, select __Connect with the Mongo Shell__, and for the __Mongo Shell version__ you have installed,  copy the __Connection String__
* Once the cluster has been fully provisioned, in the Atlas console, click the **... (*ellipsis*)** for the cluster, select **Load Sample Dataset**. In the modal dialog, confirm that you want to load the sample dataset by choosing **Load Sample Dataset**

__2. Configure An Atlas Scheduled Trigger For Performing Incremental Analytics__
* In the Atlas console, select __Triggers__ under the _Services_ group in left menu and click the <font style="color:green">__Add Trigger__</font> button, specifying the following fields in the trigger configuration page before then pressing __Save__
  - __Trigger Type__   : Scheduled
  - __Name__           : UpdateReport
  - __Scheduled Type__ : Basic
  - __Repeat Once By__ : Minute _every_ 1
  - __Link Clusters__  : Select your new M10 cluster name and click the __Link__ button
  - __Function__       : Copy and paste the contents of the [report-generator.js](report-generator.js) file from the base folder of this proof and edit the JavaScript field __\<cluster name\>__ with the name of your cluster before saving

__3. Create a Stitch Chart to Observe the Incremental Analytics Updates as the Scheduled Trigger Fires__

&nbsp;&nbsp;&nbsp;&nbsp;__Add Charts Data Source:__

* Select __Charts__ option on the left-hand menu in Atlas
* Select the **Data Sources** tab
* Select the <font style="color:green">**New Data Source**</font> button
* Select your cluster and press connect
* From the resulting list, select the **sample_supplies [ ]** database and enable the checkbox for it (ensure both a _sales_ collection + the new _reports_ collection generated by the just confirued trigger are displayed) before clicking the <font style="color:green">**Set Permissions**</font> button
* Click the <font style="color:green">**Publish Data Source**</font> button to complete setting up the data source.

&nbsp;&nbsp;&nbsp;&nbsp;__Add Charts Dashboard:__

* Select _Dashboards_ tab and click the <font style="color:green;">__New Dashboard__</font> button and name the new dashboard __Sales Report__ and click <font style="color:green">__Create__</font>
* Select <font style="color:green;">__Add Chart__</font>
* From the **[Choose a Data Source]** dropdown and select the __sample_supplies.report__ collection data source.
* Drag the **sales** field to the X Axis (aggregation)
* Drag the **_id.year** field to the Y Axis, and disable _BINNING_
* Drag the **_id.location** field to the Series
* Click the <font style="color:green">**Save and Close**</font> button.
* Expand the dashboard if desired
* Select the **AUTO** button dropdown, and set Auto Refresh Settings to _1 minute_.

__4. Connect MongoDB Command Tools To Atlas Cluster From Laptop__
* Ensure MongoDB version 4.2+ is already installed your laptop, mainly to enable MongoDB command line tools to be used (no MongoDB databases will be run on the laptop for this proof)
* Run the following from a command line terminal on your laptop to check that Mongo shell can connect to the Atlas database (change the _PASSWORD_ string to match your password and change the Cluster SRV URL to the connection string you made a note of earlier):
  ```bash
  mongo "mongodb+srv://main_user:PASSWORD@testcluster-a1234z.mongodb.net/sample_supplies" --eval 'db.version()'
  MongoDB shell version v4.2.1
  connecting to:
  ...
  MongoDB server version: 4.2.1
  4.2.1
  ```
* Keep this command line terminal open ready for the Execution phase

---
## Execution

__1. Run the Continuous Generate Sales Script__

###### NOTE: If you've run the _generate-sales.js_ script and want to reset your _sales_ sample data to the original state, you can execute the __reset-sales.js__ script from the Mongo Shell to delete the generated data.

From the open command line terminal, ensure the current directory is the base folder of this proof and then run the following script to continuously generate new sales data using the Mongo Shell (replace the _PASSWORD_ string and the Cluster SRV URL accordingly, and __very importantly__, ensure the the database name at the end of the URL is __sample_supplies__, otherwise data will not be added to the right collection:

```
mongo "mongodb+srv://main_user:PASSWORD@testcluster-a1234z.mongodb.net/sample_supplies" generate-sales.js
```
```
MongoDB shell version v4.2.1
connecting to: ...
MongoDB server version: 4.2.1
[{"gender":"M","age":42,"email":"cauho@witwuta.sv","satisfaction":4}]
["Denver","London","Austin","Seattle","New York","San Diego","Chicago","Tampa"]
["Online","In store","Phone"]
setting random seed: 3739356571
Sun Dec 31 2017 19:00:00 GMT-0500 (EST)
{ "inserted" : 5 }
```
###### __NOTE__: The script uses the existing data in the _sample\_supplies.sales_ collection to generate new sales documents randomly, and inserts a few every second. The script will run for about 20 minutes inserting new raw records the into the _sample\_supplies.sales_ collection, which should be plenty of time to observe the updates to the incremental analytics stored in the _sample\_supplies.report_ collection.

__2. Return to your Charts page__

You should notice the chart updating every minute and the sales for 2018 and beyond will be incrementally increasing.  If you are impatient, you can click the <font style="color:green;">__Auto__</font> button to force an instant refresh of the chart.

---
## Measurement

After the trigger first fires, it will have created the documents in the _report_ collection. The chart will display the current report data and will refresh showing the current data in the _report_ collection every minute. To prove the incremental analytics process lifecycle is working, observe the chart over at least 3 minutes and show that it changes roughly every minute to reflect the modified _report_ collection.

![Charts image](img/results.png)

__NOTE:__ Since the [$merge](https://docs.mongodb.com/manual/reference/operator/aggregation/merge/) does not return results, it can be hard to see what actually happened. If you want to get more visibility of this, see the tips [here](tips.md)
