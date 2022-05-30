# TIPS FOR UNDERSTANDING THE DATABASE TRIGGER MERGE PROCESS

Since the [$merge](https://docs.mongodb.com/manual/reference/operator/aggregation/merge/) does not return results, it can be hard to see what actually happened. Add a database trigger for Insert/Update/Delete/Replace to the _report_ collection and store the [ChangeEvent](https://docs.mongodb.com/manual/reference/change-events/) in a collection:
* Triggers : [Add Trigger]
* Trigger Type : Database
* Name : changeEventTrigger
* Select Linked Cluster : <Your Cluster Name>
* Database Name : sample_supplies
* Collection Name : report
* Operation Type : select all - Insert Update Delete Replace
* FUNCTION:
```
exports = async function(changeEvent) {
  const events = context.services.get( <Linked Cluster> ).db("sample_supplies").collection( "events" );
  const result = await events.insertOne( changeEvent );
  return { 'result' : result };
};
```
* Hit the <font style="color:green" >[Save]</font> button.  

Now, changes to the __report__ documents will get logged as documents in the __events__ collection:
```
MongoDB Enterprise IGNITE-shard-0:PRIMARY> db.events.aggregate( [{$group : { _id : "$operationType", count : { $sum : 1 } } }  ] )
{ "_id" : "insert", "count" : 108 }
{ "_id" : "update", "count" : 62 }
```
