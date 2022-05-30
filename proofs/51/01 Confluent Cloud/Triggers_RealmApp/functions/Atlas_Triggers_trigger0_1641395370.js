exports = function(changeEvent) {
  const fullDocument = changeEvent.fullDocument;
  
  const mongodb = context.services.get('Cluster1');
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