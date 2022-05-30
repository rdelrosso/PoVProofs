# GEOSPATIAL

__Ability to search for records based on Earth geospatial location data, without requiring full data-set scans, and including the sphere-aware query types of 1) radial distance from a point, 2) shaped areas which a point occurs in, and 3) contained within a shaped area__

__SA Maintainer__: [Paul Done](mailto:paul.done@mongodb.com) <br/>
__Time to setup__: 30 mins <br/>
__Time to execute__: 15 mins <br/>


---
## Description

This proof shows how MongoDB's Geospatial capabilities can be leveraged to find geographical locations and sites of interest via simple query operators. These will employ geospatial 2-D spherical aware indexes, for low latency and accurate responses. 

In this specific example, the needs of a roaming mobile phone user will be simulated, where the user wants to quickly locate the nearest airports to their current GPS location. Two database collections will be utilised, one representing all the main airports in the world and their geospatial locations, and the other representing all the countries in the world and their geospatial shapes (polygons composed of a series of geospatial coordinates defining the countries' borders). 

For this proof's 3 main criteria, the following MongoDB GeoSpatial query operators will be leveraged, employing a 2-D spherical index that has first been defined for each of the two collections (_airports_ & _countries_):
 1. For the __radial distance from a point__ geospatial query: MongoDB's __$nearSphere__ query operator
 2. For the __shaped areas which a point occurs in__ geospatial query: MongoDB's __$geoIntersects__ query operator
 3. For the __contained within a shaped area__ geospatial query: MongoDB's __$geoWithin__ query operator


---
## Setup
__1. Configure Laptop__
* Ensure MongoDB version 3.6+ is already installed your laptop, mainly to enable MongoDB command line tools to be used (no MongoDB databases will be run on the laptop for this proof)
* [Download](https://www.mongodb.com/download-center/compass) and install Compass on your laptop

__2. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* Create an __M10__ based 3 node replica-set in a single cloud provider region of your choice with default settings
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Node.js version__  copy the __Connection String Only__ - make a note of this MongoDB URL address to be used later

__3. Load Data Into A Collection In The Atlas Cluster__
* Import the JSON text data representing all airports in the world (and their location coordinates) into the MongoDB database with the following command, first replacing the password and address with the values noted earlier:
  ```bash	
  mongoimport --uri "mongodb+srv://main_user:MyPassword@democluster-abcde.mongodb.net/GEOSPATIAL" -c airports airports.json
  ```
* Import the JSON text data representing all countries in the world (and their shape's border coordinates) into the MongoDB database with the following command, first replacing the password and address with the values noted earlier:
  ```bash
  mongoimport --uri "mongodb+srv://main_user:MyPassword@democluster-abcde.mongodb.net/GEOSPATIAL" -c countries countries.json
  ```
* For the deployed database cluster, in the Atlas console, click the __Connect button__, select __Connect with the Mongo Shell__, and in the __Run your connection string in your command line__ section copy the connection command line and execute it to start the Mongo Shell against the database (providing your password when prompted for), similar to below:
  ```bash
  mongo "mongodb+srv://testcluster-abcde.mongodb.net/test" --username main_user 
  ```
* In the Mongo Shell, run the following commands to define _2-D Spherical Indexes_ for the _airports_ and _countries_ collections:
  ```js
  use GEOSPATIAL
  db.airports.createIndex({geometry: "2dsphere"})
  db.countries.createIndex({geometry: "2dsphere"})
  ```
* Keep the Mongo Shell open ready to be used in the _Execution_ phase of this proof
* For the deployed database cluster, in the Atlas console, click the __Connect button__, select __Connect With MongoDB Compass__ and click the __Copy__ button to copy the connection string
* Launch Compass and when prompted select to use the __MongoDB Connection String__ detected from the clipboard, fill in the __Password__ field and then click the __Connect__ button
* In Compass, navigate to the __GEOSPATIAL__ database and in the __Documents__ tab, ensure data is shown for both the collections: __airports__ & __countries__
![docs](img/docs.png "docs")
* Keep the Compass window open ready to be used in the _Execution_ phase of this proof

    
---
## Execution

__TEST 0. Preliminary Check In Compass__
* In the __Schema__ tab of the already open Compass application, navigate to the __GEOSPATIAL.airports__ database collection, press the __Analyze__ button and in the results, check that for the __geometry__ field, a world map is displayed showing a sample subset of airports around the world. This shows that Compass has determined that one of the fields for all records contains GeoJSON based coordinates, and hence can be rendered on a world map.
* In the displayed world map, zoom into a specific area (e.g. London), click the __circle__ icon shown near the top right of the map, then click on a point in the map and then drag the mouse outwards a little. This will automatically generate a spherical query shown in the __filter__ box near the top of the screen. Press the __Analyze__ button again to execute a query based on this _$geoWithin / $centerSphere_ filter and check that the results only contain airports which are inside the drawn sphere, similar to the Compass screenshot below (for a center point based in London in this example).
![mapdrag](img/mapdrag.png "mapdrag")

__TEST 1. Geospatial query: Radial distance from a point__
* Using Google Maps on your phone, zoom into your current location (or anywhere you want in the world), and for a specific site shown, hold your finger down on the site so that Google Maps shows the GPS latitude and longitude coordinates for that site, similar to the screenshot below (which shows the location of the MongoDB office in London). Note: You can also use Google Maps from a web browser to find the coordinates of a place
![phonemap](img/phonemap.png "phonemap")
* Make a note of the _latitude,longitude_ coordinates shown near the top of the Google Maps location (e.g. _51.506625,-0.106882_ shown in this example)
* Swap the two coordinates around, because the [GeoJSON standard](http://geojson.org/) defines coordinates in the opposite order, specifically: _longitude,latitude_ (e.g. _-0.106882,51.506625_ for this example)
* In the open Mongo Shell terminal, execute the following to perform a query for all the _medium and large airports_ located within a sphere of 50KM (50,000 metres) from the site's coordinates you just identified, with the results provided in order of nearest airport first (first replace the GeoJSON coordinates in the example with the ones you recorded for your chosen site). 
  ```js
  use GEOSPATIAL;
  db.airports.find(
    {
        geometry: {
            $nearSphere: {
                $geometry: {
                    type : "Point",
                    coordinates : [-0.106882, 51.506625]
                },
                $maxDistance: 50000
            }
        },
        type: {$in: ["medium_airport", "large_airport"]}
    },
    {
        _id: 0,
        name: 1,
        type: 1,
    }
  ).pretty();
  ```
* Check the listed airports result to ensure the listed airports are indeed located near to the location you specified

__TEST 2. Geospatial query: Shaped areas which a point occurs in__
* In the open Mongo Shell terminal, execute the following to perform a query to find which country your current stated point coordinates is located in, by finding which country's polygon your location intersects with (first replace the GeoJSON coordinates in the example with the ones you recorded for your chosen site)
  ```js
  use GEOSPATIAL;
  current_country = db.countries.findOne({geometry: {$geoIntersects: {$geometry: {type: "Point", coordinates: [-0.106882, 51.506625]}}}});
  print('Current country: ' + current_country.name);
  ```
* Check the resulting country name displayed is indeed the country where the site you specified is located in

__TEST 3. Geospatial query: Contained within a shaped area__
* In the open Mongo Shell terminal, execute the following to perform a query to find all the _large airports_ that are located in the country which your current stated location occurs in. This is achieved by finding all the airports' coordinates that are within the polygon coordinates of the country's border (note, this uses the `current_country` variable from the previous test to identify the border coordinates of the country containing your current stated location).
  ```js
  use GEOSPATIAL;
  db.airports.find(
    {
        geometry: {
            $geoWithin: {
                $geometry: {
                    type: current_country.geometry.type,
                    coordinates: current_country.geometry.coordinates
                }
            }
        },
        type: "large_airport"
    },
    {
        '_id': 0,
        'type': 1, 
        'name': 1, 
    }
  );
  ```
* Check the resulting list of airports are indeed located within the country containing the site location you specified
 

---
## Measurement

Upon completion of the 3 main tests, the following results should be captured:

  - __TEST 1. Geospatial query: Radial distance from a point__: The listed airports should all be the nearest main airports to the location you specified, with nearest first, which for the example MongoDB London Office Location should look like the following:
  ```js
  { "type" : "medium_airport", "name" : "London City Airport" }
  { "type" : "medium_airport", "name" : "London Biggin Hill Airport" }
  { "type" : "medium_airport", "name" : "RAF Northolt" }
  { "type" : "large_airport", "name" : "London Heathrow Airport" }
  { "type" : "large_airport", "name" : "London Gatwick Airport" }
  { "type" : "large_airport", "name" : "London Luton Airport" }
  { "type" : "large_airport", "name" : "London Stansted Airport" }
  ```
  - __TEST 2. Geospatial query: Shaped areas which a point occurs in__: The listed country name should be the country where the site you specified is located, which for the example MongoDB London Office Location should be the following:
  ```js
  Current country: United Kingdom
  ```
  - __TEST 3. Geospatial query: Contained within a shaped area__: The listed airports should all be located in the country containing the site you specified, which for the example MongoDB London Office Location should be the following:
  ```js
  { "type" : "large_airport", "name" : "RAF Mildenhall" }
  { "type" : "large_airport", "name" : "RAF Lakenheath" }
  { "type" : "large_airport", "name" : "London Stansted Airport" }
  { "type" : "large_airport", "name" : "Norwich International Airport" }
  { "type" : "large_airport", "name" : "George Best Belfast City Airport" }
  { "type" : "large_airport", "name" : "Belfast International Airport" }
  { "type" : "large_airport", "name" : "Exeter International Airport" }
  { "type" : "large_airport", "name" : "Cardiff International Airport" }
  { "type" : "large_airport", "name" : "Birmingham International Airport" }
  { "type" : "large_airport", "name" : "RAF Brize Norton" }
  { "type" : "large_airport", "name" : "RAF Fairford" }
  { "type" : "large_airport", "name" : "Bristol Airport" }
  { "type" : "large_airport", "name" : "Bournemouth Airport" }
  { "type" : "large_airport", "name" : "Southampton Airport" }
  { "type" : "large_airport", "name" : "London Gatwick Airport" }
  { "type" : "large_airport", "name" : "London Luton Airport" }
  { "type" : "large_airport", "name" : "London Heathrow Airport" }
  { "type" : "large_airport", "name" : "Robin Hood Doncaster Sheffield Airport" }
  { "type" : "large_airport", "name" : "Leeds Bradford Airport" }
  { "type" : "large_airport", "name" : "East Midlands Airport" }
  { "type" : "large_airport", "name" : "Manchester Airport" }
  { "type" : "large_airport", "name" : "Liverpool John Lennon Airport" }
  { "type" : "large_airport", "name" : "Newcastle Airport" }
  { "type" : "large_airport", "name" : "Aberdeen Dyce Airport" }
  { "type" : "large_airport", "name" : "Edinburgh Airport" }
  { "type" : "large_airport", "name" : "Glasgow International Airport" }
  { "type" : "large_airport", "name" : "[Duplicate] Pic" }
  ```

