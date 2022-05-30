exports = async function() {
  const cntx = context.services.get("<Linked Cluster>");
  const db = cntx.db("sample_supplies");
  const coll = db.collection("sales");
  const report = db.collection("report");
  const now = new Date();

   /*
  / This function generates aggregated sales data in the 'report' collection,
  / recording the most recent sale date in the 'last_sale' field. The 'last_sale' 
  / value is used in future calls to determine the sale date from which grab
  / the incremental records for the merge operation.   
  */
 var t0 = new Date(0);
 var last_sales = (await report.aggregate( [ { $group : { _id : null, t0 : { $max : "$last_sale"} } } ] ).toArray());
 if( last_sales.length ) {
   t0 = last_sales[0].t0;
 }
 console.log ("Last sale date: ", t0);
 // aggregate all sales more recent than last saleDate seen, and merge into 'report' collection

 // Match all documents since the last sale date...
 var stage1 = { $match : { saleDate : { $gt : new Date( t0 ) } } }
 
 // Add 'total' and 'item_count' fields...
 var stage2 = { $addFields : {
         total : { $sum : {
           $map : {
             input : "$items",
             as : "row",
             in : { $multiply : ["$$row.price", "$$row.quantity"] }
           }
         }
       },
         item_count : {
           $sum : { $size : "$items" }
         }
       }
     }
     
 // Calculate average number of items and total sales per month by location and channel
 var stage3 =  { $group : {
         _id : {
           year : { $year : "$saleDate" },
           month : { $month : "$saleDate" },
           location: "$storeLocation",
           channel : "$purchaseMethod"
         },
         avg_count : { $avg : "$item_count" },
         sales : { $sum : "$total" },
         last_sale : { $max : "$saleDate" }
       }
     }
     
 // Record the update time
 var stage4 = { $addFields : { 'updateTime' : now } }
 
 // Sort by sale date, location and channel
 var stage5 = { $sort : { _id : 1 } }
 
 // Merge into report materialized view
 var stage6 = { $merge : {
         into : "report",
         on : "_id",
         whenMatched : "merge",
         whenNotMatched : "insert"
       }
     }

 var res = coll.aggregate([stage1, stage2, stage3, stage4, stage4, stage5, stage6])
     .toArray().then( console.log( "Finished merge pipeline..." ));
     
 return { 'updateCount' : await report.count( { 'updateTime' : { $gte : now } } ) };
};
