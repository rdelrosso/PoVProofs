exports = function (changeEvent) {
  const docId = changeEvent.documentKey._id;
  const fullDocument = changeEvent.fullDocument;
  const collection = context.services.get("mongodb-atlas").db("sample_airbnb").collection("listingsAndReviews");

  console.log("checking booking update...");
  console.log(JSON.stringify(fullDocument));

  if (fullDocument.bookingRequests.length == 1) {
    console.log("checking initial booking request...")
    if (fullDocument.bookingRequests[0].booked && !fullDocument.bookingRequests[0].confirmed) {

      const query = {
        "_id": docId,
        "bookingRequests.bookedByUserId": fullDocument.bookingRequests[0].bookedByUserId
      };

      const update = {
        $set:
        {
          "bookingRequests.$.confirmed": true,
          "bookingRequests.$.confirmedAt": new Date()
        }
      };

      const options = { "upsert": false };

      collection.updateOne(query, update, options)
        .then(result => {
          const { matchedCount, modifiedCount } = result;
          if (matchedCount && modifiedCount) {
            console.log("approved booking request...")
          }
        })
        .catch(err => console.error(`Failed to update the doc: ${err}`))
    }
  } else if (fullDocument.bookingRequests.length > 1) {
    console.log("ignoring new booking request...")

  } else {
    console.log("booking cancelled...")
  }
};