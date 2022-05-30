const { MongoClient } = require("mongodb");
const fetch = require('node-fetch');

const uri = process.argv.slice(2)[0];
const client = new MongoClient(uri, { useUnifiedTopology: true });

const insertDocuments = async (collection) => {
    let counter = 1;
    while(counter < 100){
        console.group("Inserting document - " + counter);
        console.time('Time taken');
        const doc = { documentNumber: counter};
        const result = await collection.insertOne(doc);                
        console.timeEnd('Time taken');                    
        let ip = result.connection.address.substring(0, result.connection.address.length-6);;
        const response = await fetch('http://ip-api.com/json/' + ip);
        const json = await response.json();
        console.log("Connected to: " + result.connection.address + ": " + json.org) ;
        console.groupEnd("Inserting document - " + counter);
        await timeout(3000);
        counter++;
    }
  }

const timeout = (ms) => {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const run = async () => {
    try{
        await client.connect();
        const database = client.db("test");
        const collection = database.collection("records");        
        await insertDocuments(collection);
        await client.close();        
    }catch (e) {
        console.error(e);
    }        
}
run();
