# TRANSACTION

__Ability to update multiple different records as part of a single ACID transaction which is guaranteed to either succeed or fail as a whole__

__SA Maintainer__: [Britton LaRoche](mailto:britton.laroche@mongodb.com) <br/>
__Time to setup__: 15 mins <br/>
__Time to execute__: 15 mins <br/>


---
## Description

This proof shows how MongoDB is able handle multi document ACID compliant transactions, implemented in a way that is idiomatic to your chosen programming language, in a way that feels familiar to anyone who has used relational databases. A transaction allows a series of insert and update operations to be applied across multiple different documents which are committed together upon successful completion of all steps, or completely rolled back, if an error occurs. A transaction in a database system must maintain Atomicity, Consistency, Isolation, and Durability (ACID), in order to ensure accuracy, completeness, and data integrity. For more information, see the online [MongoDB Transactions documentation](https://docs.mongodb.com/manual/core/transactions/)

Our example will focus on a __fictitious online game that requires transactions__ for the following activities: trades made between players, new game referrals and updates to the documents which represent player characters.  If all the commands in the transaction are successful the updates and inserts to different player documents are committed and the changes are permanent.  If any errors occur the transaction is rolled back and the player data remains unchanged.

![Game](img/game.jpg "Game")


---
## Setup
__1. Configure Laptop__
* Ensure MongoDB version __4.0+__ is already installed your laptop, mainly to enable MongoDB command line tools to be used (no MongoDB databases will be run on the laptop for this proof)

__2. Configure Atlas Environment__
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user called __main_user__, and for __User Privileges__ specify __Read and write to any database__ (make a note of the password you specify)
* Create an __M10__ based 3 node replica-set in a single cloud provider region of your choice with default settings
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address

__3. Start the MongoDB Shell and Connect to your Atlas Cluster__
* You must use **mongosh** to run this proof point. If you haven't done so yet, please [install mongosh](https://docs.mongodb.com/mongodb-shell/install/) before continuing.
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect with the Mongo Shell__, and in the __Run your connection string in your command line__ section copy the connection command line - make a note of this connection command line
* __IMPORTANT__: Before the Mongo Shell is started, run the following command:

  `bash setup-env.sh`
  
  The above command loads the Mongo Shell with a variable containing your Operating System username.  All non-alphanumeric characters are removed.  This variable will be used to configure a unique namespace (database and collection) to avoid any conflicts with other SAs performing this demo.

* From a command line terminal on your laptop, launch the Mongo Shell using the Atlas cluster connection command you just captured, and when prompted, provide the password that you specified in an earlier setup step, for example:
  ```bash
  mongosh "mongodb+srv://testcluster-x123x.mongodb.net/test" --username main_user 
  ```

__4. Create a Database and Insert Some Initial Data__
* Using the Shell create the _TRANSACTIONS_ database and populate a collection that uses the username of the logged in user (to avoid collisions), by inserting player documents into the collection, and then create a unique index on the player name, so no two players can have the same name in the game:

  ```js
  // Create collection in the TRANSACTIONS database with 2 Players 
  use TRANSACTIONS;

  // Set collName to OS username. collName will be used to reference collection name throughout this proof.
  var collName = process.env.USER
  print('Using DB.Collection: ' + db + '.' + collName)

  // Drop collection if it exists
  db[collName].drop()

  db[collName].insert({"name": "Zoltar", "class": "Mage", "Gold": 100, "Apples": 10 });
  
  db[collName].insert({"name": "Gilgamesh", "class": "Ranger", "Gold": 100, "Apples": 10});
  
  db[collName].createIndex( { "name": 1 }, { unique: true } );
  ```
    

---
## Execution
Run each of the following tests sequentially via the Mongo Shell (note later tests may rely on earlier tests having been first run, so ensure you run the tests in order).

### TEST 1: Session Isolation
Multiple sessions are a natural part of database activity as multiple users and processes access the same data at the same time. In this example we create two new sessions _s1_ and _s2_. Session _s1_ will create a new player that will not be visible to session _s2_ until the transaction has been committed. Here we demonstrate read isolation between sessions until data is committed. To provide an isolation level of snapshot with repeatable read from a majority of updated replicas, the following settings are made in the code below on the transaction `s1.startTransaction({readConcern: {level: 'snapshot'}, writeConcern: {w: 'majority'}})`
  ```js

  // Create two sessions, s1 and s2 and start a transaction with s1
  var s1 = db.getMongo().startSession();
  var s2 = db.getMongo().startSession();
  var s1Player = s1.getDatabase('TRANSACTIONS').getCollection(collName);
  var s2Player = s2.getDatabase('TRANSACTIONS').getCollection(collName);
  s1.startTransaction({readConcern: {level: 'snapshot'}, writeConcern: {w: 'majority'}});
  
  // Insert player 3, inside a transaction/session1
  s1Player.insert({"name": "Merlin", "class": "Mage", "Gold": 100, "Apples": 10});
  
  // Use session 2 and find the documents from collection and session1
  s2Player.find();
  // EXPECTED RESULT:
  // {"name": "Zoltar", "class": "Mage", "Gold": 100, "Apples": 10 }
  // {"name": "Gilgamesh", "class": "Ranger", "Gold": 100, "Apples": 10}
  
  // Notice that the insert on session1 is only visible to it.
  s1Player.find()
  // EXPECTED RESULT:
  // {"name": "Zoltar", "class": "Mage", "Gold": 100, "Apples": 10 }
  // {"name": "Gilgamesh", "class": "Ranger", "Gold": 100, "Apples": 10}
  // {"name": "Merlin", "class": "Mage", "Gold": 100, "Apples": 10}"}
  
  // Commit & end the session (if not committed within 60 secs transaction will timeout)
  s1.commitTransaction();
  
  // show the documents after committing the transaction
  s2Player.find();
  // EXPECTED RESULT:
  // {"name": "Zoltar", "class": "Mage", "Gold": 100, "Apples": 10 }
  // {"name": "Gilgamesh, "class": "Ranger", "Gold": 100, "Apples": 10}
  // {"name": "Merlin, "class": "Mage", "Gold": 100, "Apples": 10}"}
  ```

__RESULT 1__: Before the transaction commits, _s2player_ should not see the newly added _Merlin_ record, but after the transaction is committed it should be visible to _s2player_

Here the transaction was committed but because the default transaction timeout is 60 seconds, the transaction would be timed-out and automatically aborted if the above code is not executed quickly enough. This is desired behaviour for transactions in the real world to prevent long running transactions from excessively consuming system resources.


### TEST 2: Multiple Document Updates, Atomicity and Session Isolation
In the game Merlin decides to buy an apple from Zoltar for 2 gold.  This is an exchange of in game currency and items across two player documents. The transaction occurs in session 1 and the updated information is not available in other sessions until the commit is final.  Should an error occur the transaction is rolled back. Here we demonstrate both isolation and the atomicity of the transaction, neither document is actually updated until the changes on both documents are committed.
  ```js
  // Start transaction with Merlin buying an apple from Zoltar for 2 gold
  s1.startTransaction({readConcern: {level: 'snapshot'}, writeConcern: {w: 'majority'}});
  s1Player.updateOne({"name": "Zoltar"}, {"$inc": {"Gold": 2, "Apples": -1} });
  s1Player.updateOne({"name": "Merlin"}, {"$inc": {"Gold": -2, "Apples": 1} });
  
  s1Player.find();
  // EXPECTED RESULT:
  // {"name": "Zoltar", "class": "Mage", "Gold": 102, "Apples": 9 }
  // {"name": "Gilgamesh, "class": "Ranger", "Gold": 100, "Apples": 10}
  // {"name": "Merlin, "class": "Mage", "Gold": 98, "Apples": 11}"}
  
  s2Player.find();
  // EXPECTED RESULT:
  // {"name": "Zoltar", "class": "Mage", "Gold": 100, "Apples": 10 }
  // {"name": "Gilgamesh, "class": "Ranger", "Gold": 100, "Apples": 10}
  // {"name": "Merlin, "class": "Mage", "Gold": 100, "Apples": 10}"}
  
  s1.commitTransaction();
  
  s2Player.find();
  // EXPECTED RESULT:
  // {"name": "Zoltar", "class": "Mage", "Gold": 102, "Apples": 9 }
  // {"name": "Gilgamesh, "class": "Ranger", "Gold": 100, "Apples": 10}
  // {"name": "Merlin, "class": "Mage", "Gold": 98, "Apples": 11}"}
  ```

__RESULT 2__: Before the transaction commits, _s2player_ should see the older values of _gold_ and _apples_ for both _Zoltar_ and _Merlin_, but after the transaction is committed the new values should be visibile to _s2player_


### TEST 3: Multiple Document Updates with Atomicity, Consistency with a Rollback
In this example Zoltar refers a friend. Any friend who successfully creates an account yields a 10 gold reward to the player who referred the friend. Unaware that the name "Merlin" was taken, Zoltar's friend fails to create an account, the transaction is rolled back and Zoltar's player data remains unchanged, he never receives the 10 gold bonus. Here we demonstrate atomicity and consistency as the player data is protected by a rollback when an error occurs.
  ```js
  // Start a transaction with Zoltar refers a friend and gets 10 gold for the account creation
  s1.startTransaction({readConcern: {level: 'snapshot'}, writeConcern: {w: 'majority'}});
  
  s1Player.find({"name": "Zoltar"});
  // EXPECTED RESULT:
  // {"name": "Zoltar", "class": "Mage", "Gold": 102, "Apples": 9 }
  
  s1Player.updateOne({"name": "Zoltar"}, {"$inc": {"Gold": 10} });
  
  s1Player.find({"name": "Zoltar"});
  // EXPECTED RESULT:
  // {"name": "Zoltar", "class": "Mage", "Gold": 112, "Apples": 9 }
  
  s1Player.insert({"name": "Merlin", "class": "Wizard", "Gold": 100, "Apples": 10 });
  // EXPECTED RESULT:
  // WriteCommandError({
  //        "operationTime" : Timestamp(1549657865, 3),
  //        "ok" : 0,
  //        "errmsg" : "E11000 duplicate key error collection: game.player index: name_1 dup key: { : \"Merlin\" }",
  //        "code" : 11000,
  //        "codeName" : "DuplicateKey",
  // })
  
  s1.abortTransaction();
  
  s1Player.find({"name": "Zoltar"});
  // EXPECTED RESULT:
  // {"name": "Zoltar", "class": "Mage", "Gold": 102, "Apples": 9 }
  ```

__RESULT 3__: Before the transaction commits, _s1player_ should see the seemingly updated _gold_ value of _112_ for _Zoltar_, but once the transaction has aborted and hence rolled back, the original value should be seen


### TEST 4: Multiple Document Updates and Retries Leading to Commit
Zoltar's friend tries again to create the account after receiving the error that the name "Merlin" was taken. He retries with a new player name of "Tim" and he is successful. When the transaction commits Zoltar gets the 10 gold. Session 2 can not see the change until the commit completes.
  ```js
  // Start a transaction with Zoltar refers a friend and gets 10 gold for the account creation
  s1.startTransaction({readConcern: {level: 'snapshot'}, writeConcern: {w: 'majority'}});
  
  s1Player.find({"name": "Zoltar"});
  // EXPECTED RESULT:
  // {"name": "Zoltar", "class": "Mage", "Gold": 102, "Apples": 9 }
  
  s1Player.updateOne({"name": "Zoltar"}, {"$inc": {"Gold": 10} });
  
  s1Player.find({"name": "Zoltar"});
  // EXPECTED RESULT:
  // {"name": "Zoltar", "class": "Mage", "Gold": 112, "Apples": 9 }
  
  s2Player.find({"name": "Zoltar"});
  // EXPECTED RESULT:
  // {"name": "Zoltar", "class": "Mage", "Gold": 102, "Apples": 9 }
  
  s1Player.insert({"name": "Tim", "class": "Wizard", "Gold": 100, "Apples": 10 });
  
  s1.commitTransaction();
  
  s2Player.find({"name": "Zoltar"});
  // EXPECTED RESULT:
  // {"name": "Zoltar", "class": "Mage", "Gold": 112, "Apples": 9 }
    
  ```

__RESULT 4__: Before the transaction commits, _s1player_ should see the seemingly updated _gold_ value of _112_ for _Zoltar_ and _s2player_ should still see the original value, but once the transaction has committed, the new value should be visible to _s2player_


---
## Measurement

For the four tests, the four respective __RESULT__ results shown above should be observed. In summary the observations should be:

* __RESULT 1__: Before the transaction commits, for a single update, other sessions should not see changes made by a separate transaction, and only see them when the transaction is committed
* __RESULT 2__: Before the transaction commits, for multiple updates, other sessions should not see changes made by a separate transaction, and only see them when the transaction is committed
* __RESULT 3__: Before the transaction commits, the transaction section that updates some fields should be able to see those changes, but once the transaction has aborted and rolled-back, the session should now see the original values
* __RESULT 4__: Before the transaction commits, the transaction section that updates some fields should be able to see those changes whereas the other session should only see the original values, but once the transaction has committed, all sessions should see the new values

