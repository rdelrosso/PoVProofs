// This function is the webhook's request handler.
exports = function(payload) {
  const collection = context.services.get("mongodb-atlas-fts").db("sample_mflix").collection("movies");
  
  	let arg = payload.query.arg;

  	return collection.aggregate([
  	  {$search: {
        compound: {
          must: {
            search: {
              path: 'fullplot',
              query: arg
            }
          },
          should: {
            search: {
              path: 'title',
              query: arg
            }
          }
        }
      }}, 
      {$project: {
        title: 1,
        _id: 0,
        year: 1,
        fullplot: 1,
        score: {$meta: 'searchScore'}
        
      }},
      {$limit:
        15
      }]).toArray();
};
