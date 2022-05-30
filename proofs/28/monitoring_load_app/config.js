module.exports = {
    mdb_url:"",

    //Concurrency: how many parallel threads should be doing inserts
    //increase this number to increase the workload on mongodb
    //recommended to be set equal to the number of cores on the machine running this program
    concurrency:16,
    
    //how many records should be returned by find commands
    limit:10,

    //operation frequency (milliseconds)
    writeFrequency:5,
    readFrequency:5
}
