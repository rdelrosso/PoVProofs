print( "Starting sales records:", db.sales.count() );
const TEST_LENGTH = 60 * 20 * 1000; // 20 minutes run time in ms
const MAX_BATCH_SIZE = 8;  // Maximum number of sales to generate per day

// create list of customers, locations, channels from existing data
var customers = db.sales.distinct(  "customer" );
var locations = db.sales.distinct( "storeLocation" );
// add a new Sales location
locations.push( "Tampa" );
var channels = db.sales.distinct( "purchaseMethod" );
print( "Sample customer:", JSON.stringify(customers.slice(0,1)) );
print( "Available locations:", JSON.stringify(locations ));
print( "Possible ales channels:", JSON.stringify(channels ));

const startDate   = new Date( '2018-01-01' );
const maxDate     = new Date( '2020-12-31' );
print( "Earliest sale date: ", startDate );
var dayCounter = 0; // days added to startDate for next batch of sales
var t0 = Date.now();
while( Date.now() - t0 < TEST_LENGTH ) {
  sleep( 1000 ); // 1 second

  // salesToGenerateForBatch  : number of sales to generate for a day
  const salesToGenerateForBatch  = Math.ceil( Math.random( ) * MAX_BATCH_SIZE );
  let salesBatch = [];
  let saleDate = "";

  for( var txn = 0; txn < salesToGenerateForBatch ; txn++ ) {

    // select a sample document using a random customer and remove _id
    let it = db.sales.findOne( { customer : customers[ Math.floor( Math.random( ) * customers.length ) ] }, { '_id' : 0 } );

    // replace customer, location, method, coupon and saleDate
    it.customer = customers[ Math.floor( Math.random() * customers.length ) ];
    it.storeLocation = locations[ Math.floor( Math.random() * locations.length ) ];
    it.purchaseMethod = channels[ Math.floor( Math.random() * channels.length ) ];
    it.couponUsed = (Math.floor( Math.random() * 3 ) == 1 ? true : false);

    // add days to the start date
    saleDate = new Date( startDate.valueOf() + (864E5 * dayCounter) );
    it.saleDate = saleDate;
    it.version = 2;
    salesBatch.push( it );
  }
  
  // insert batch of sales documents
  var insert_result = db.sales.insertMany( salesBatch );
  if( insert_result != undefined ) {
    print( "Inserted:", insert_result['insertedIds'].length, "sales documents for", saleDate.toLocaleDateString("en-US") ); }
  else { break; }
  dayCounter++;
}
