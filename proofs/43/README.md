# NATIVE-VISUALIZATION

__Ability to rapidly expose a graphical summary report of data to business users, where the report is periodically auto-refreshed, without requiring 3rd party BI tools__

__SA Maintainer__: [Alessandro Haag](mailto:alessandro.haag@mongodb.com) <br/>
__Time to setup__: 30 mins <br/>
__Time to execute__: 15 mins <br/>


---
## Description

This proof shows how MongoDB Charts can be used to create dynamic reports and dashboards, based on MongoDB persisted data, without requiring a 3rd party BI tool.

Using mgenerate tool, you will create data sample for a Customer Single View scenario into MongoDB database. Once the data is loaded into a MongoDB Atlas database, a dashboard and set of reports will be generated, to show how Charts can easily visualize MongoDB stored data. After the dashboard is created, you will add new data in the same collection and show that the report changes to reflect the new set of data.



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
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user, e.g. __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* Create an __M30__ based 3 node replica-set in a single cloud provider region of your choice with default settings
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Node.js version__ copy the __Connection String Only__ - make a note of this MongoDB URL address to be used in the next step

__3. Load Data Into A Collection In The Atlas Cluster__
* Generate 100,000 random JSON documents representing insurance customer 'single view' records, based on the `CustomerSingleView.json` template:

```bash
mgeneratejs CustomerSingleView.json -n 100000 | mongoimport --uri "mongodb+srv://main_user:mypassword@democluster-abcd.mongodb.net/test" -db NATIVE-VISUALIZATION --collection customers --drop
```
Paste the copied URI into the `--uri` parameter, replacing the username & password fields with those you created earlier.
<br/><br/>
__Note__: This process generates over 150Mb of data. The `mgeneratejs` process itself only takes ~5 minutes to complete but the upload process can take significantly longer if you're using a slow network connection.

__4. Check That The Collection's Data Can Be Accessed Using Compass__
* From the Atlas console click the __Connect button__, select __Connect With MongoDB Compass__ and click the __Copy__ button to copy the connection string
* Launch Compass and when prompted select to use the __MongoDB Connection String__ detected from the clipboard, fill in the __Password__ field as required and then click the __Connect__ button
* In Compass, navigate to the __NATIVE-VISUALIZATION.customers__ collection and select the __Schema__ tab, press the __Analyze Schema__ button and ensure some result data is shown


---
## Execution

We will use Charts to create the dashboard "Customer Single View".

__1. Launch Charts, define a data source create the dashboard:__
* From Atlas consoleinterface, click on the Charts button.
* In the main window of Charts interface, click on the __Data Source__ tab then the _New Data Source_ button, choose your Atlas cluster and select to _Create_
* Select the _NATIVE-VISUALIZATION.customers_ collection by selecting to tick/check the box next to it then click the _Set Permissions_ button, then select every in your project then click the _Publish Data Source_ button. Uou will see a new Data Source called _NATIVE-VISUALIZATION.customers_:

![img1](img/img1.png)

* Then, go back to main Chart page and click on New Dashboard button to create a new dashboard called "Customer Single View", with no Description

__2. Creation of reports in the dashboard__
* Click the _Dashboards_ tab , then click the _New Dashboard_ button and give the Dashboard any name you want
* Click the _Add Chart_ button and in the _Choose a Data Source_ dropdown, at the top-left of the chart builder, select NATIVE-VISUALIZATION.customers.
* Specify the _Chart Type_ of __Column__
* Select the panel labeled _Stacked_ below the Chart Type dropdown menu.
* Drag the _lastname_ field from the Fields section of the Chart Builder view to the _X Axis_ encoding channel.
* In the lastname _Sort By_ dropdown, select _Value_
* Switch on _Limit Results_ and leave on default value of 10
* Drag the _policies.value_ field to the Y Axis encoding channel (the Y Axis encoding channel determines which field to use for the chart’s aggregation)
* In the _policies.value_ _Array Reductions - policies_ dropdown, select Unwind Array
* Leave the Aggregate dropdown menu for the Y Axis encoding channel on its default value of sum (this value directs the aggregation operation to return the total value of policies for each customer)
 * As shown in the screenshot below, customize the report to have the chart title __Best 10 Clients__, in the _Customize_ tab if the _Chart Type_ change the x-axis title of __Client Last Name__ and the y-axis title of __Total Value of Policies__ and for the _Y-axis_ set _Number Formatting_ to __MILLIONS__ 

![img2](img/img2.png)

* Click the _Save and Close_ button
* Next create a report that shows the __Number of Policies per State__. Do this using the _address.state_ as the location and the _policies.address.state_ for the color (_unwind_ the array and use the _count_). In order to map the data to the correct scheme, navigate to _Customize_ and change the _Shape Scheme_ to _US STATES_. Also remember to rename the labels and title appropriatly.

![img3](img/img3.png)

* Finally create a Text chart and use the _Number_ option to diplay the total value of all policies (use _policies.value_, unwinding the array and using the _sum_).

![img4](img/img4.png)

* Back in the Dashboard use _drag&drop_ to rearrange the reports to look similar to the following:

![img5](img/img5.png)

* At the top of the dashboard, from the dropdown select __Disable Auto Refresh__ (so that any data change impacting the charts can be proved in the _Measurement_ section next

---
## Measurement

* To verify the real-time update of reports in the dashboard, open a shell and execute the command again (replacing the password and URI with the ones that match your environment):

```bash
mgeneratejs CustomerSingleView.json -n 100000 | mongoimport --uri "mongodb+srv://main_user:mypassword@democluster-abcd.mongodb.net/test" -db NATIVE-VISUALIZATION --collection customers --drop
```

* Return to the Dashboard, click the __refresh__ button and verify that the contents of the report change to reflect the new data set values

