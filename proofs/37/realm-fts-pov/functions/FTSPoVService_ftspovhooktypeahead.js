// This function is the webhook's request handler.
exports = function(payload) {
  const collection = context.services.get("mongodb-atlas-fts").db("sample_mflix").collection("movies");
  

    let arg = payload.query.arg + "*";

    return collection.aggregate(
      //PASTE AGG PIPELINE CODE HERE
      [
        {$search: { 
          "index": "ix_autocomplete",
            "autocomplete": {
              "query": arg,
              "path": "title",
              "tokenOrder": "any"
            }
        }}, 
        {$project: { 
          title: 1, 
          _id: 0, 
          year: 1, 
          fullplot: 1 
        }}, 
        {$limit: 15}
      ]      
    ).toArray();
};
