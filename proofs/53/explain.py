{ explainVersion: '1',
  stages: 
   [ { '$cursor': 
        { queryPlanner: 
           { namespace: 'TIMESERIES.system.buckets.cryptoTS',
             indexFilterSet: false,
             parsedQuery: {},
             queryHash: '8B3D4AB8',
             planCacheKey: 'D542626C',
             maxIndexedOrSolutionsReached: false,
             maxIndexedAndSolutionsReached: false,
             maxScansToExplodeReached: false,
             winningPlan: { stage: 'COLLSCAN', direction: 'forward' },
             rejectedPlans: [] },
          executionStats: 
           { executionSuccess: true,
             nReturned: 1328,
             executionTimeMillis: 4263,
             totalKeysExamined: 0,
             totalDocsExamined: 1328,
             executionStages: 
              { stage: 'COLLSCAN',
                nReturned: 1328,
                executionTimeMillisEstimate: 0,
                works: 1330,
                advanced: 1328,
                needTime: 1,
                needYield: 0,
                saveState: 63,
                restoreState: 63,
                isEOF: 1,
                direction: 'forward',
                docsExamined: 1328 } } },
       nReturned: 1328,
       executionTimeMillisEstimate: 122 },
     { '$_internalUnpackBucket': 
        { include: [ 'close', 'high', 'low', 'open', 'timestamp', 'metadata' ],
          timeField: 'timestamp',
          metaField: 'metadata',
          bucketMaxSpanSeconds: 86400 },
       nReturned: 1148147,
       executionTimeMillisEstimate: 621 },
     { '$group': 
        { _id: 
           { symbol: '$metadata.symbol',
             timestamp: 
              { '$dateTrunc': 
                 { date: '$timestamp',
                   unit: { '$const': 'day' },
                   binSize: { '$const': 1 } } } },
          close: { '$last': '$close' },
          open: { '$first': '$open' },
          high: { '$max': '$high' },
          low: { '$min': '$low' } },
       maxAccumulatorMemoryUsageBytes: { close: 32040, open: 38448, high: 38448, low: 38448 },
       totalOutputDataSizeBytes: 443754,
       usedDisk: false,
       nReturned: 801,
       executionTimeMillisEstimate: 4252 },
     { '$project': 
        { high: true,
          low: true,
          open: true,
          close: true,
          timestamp: '$_id.timestamp',
          symbol: '$_id.symbol',
          _id: false },
       nReturned: 801,
       executionTimeMillisEstimate: 4252 },
     { '$sort': { sortKey: { symbol: 1, timestamp: 1 } },
       totalDataSizeSortedBytesEstimate: 356445,
       usedDisk: false,
       nReturned: 801,
       executionTimeMillisEstimate: 4252 },
     { '$_internalSetWindowFields': 
        { partitionBy: '$symbol',
          sortBy: { timestamp: 1 },
          output: 
           { AvgPrice50: { '$avg': '$close', window: { range: [ -50, 0 ], unit: 'day' } },
             AvgPrice200: 
              { '$avg': '$close',
                window: { range: [ -200, 0 ], unit: 'day' } } } },
       maxFunctionMemoryUsageBytes: { AvgPrice50: 832, AvgPrice200: 3232 },
       maxTotalMemoryUsageBytes: 76519,
       usedDisk: false,
       nReturned: 801,
       executionTimeMillisEstimate: 4262 },
     { '$match': { timestamp: { '$gte': 2020-01-01T00:00:00.000Z } },
       nReturned: 686,
       executionTimeMillisEstimate: 4262 } ],
  serverInfo: 
   { host: 'atlas-mla5fa-shard-00-02.da1ep.mongodb.net',
     port: 27017,
     version: '5.0.5',
     gitVersion: 'd65fd89df3fc039b5c55933c0f71d647a54510ae' },
  serverParameters: 
   { internalQueryFacetBufferSizeBytes: 104857600,
     internalQueryFacetMaxOutputDocSizeBytes: 104857600,
     internalLookupStageIntermediateDocumentMaxSizeBytes: 104857600,
     internalDocumentSourceGroupMaxMemoryBytes: 104857600,
     internalQueryMaxBlockingSortMemoryUsageBytes: 104857600,
     internalQueryProhibitBlockingMergeOnMongoS: 0,
     internalQueryMaxAddToSetBytes: 104857600,
     internalDocumentSourceSetWindowFieldsMaxMemoryBytes: 104857600 },
  command: 
   { aggregate: 'system.buckets.cryptoTS',
     pipeline: 
      [ { '$_internalUnpackBucket': 
           { timeField: 'timestamp',
             metaField: 'metadata',
             bucketMaxSpanSeconds: 86400,
             exclude: [] } },
        { '$group': 
           { _id: 
              { symbol: '$metadata.symbol',
                timestamp: { '$dateTrunc': { date: '$timestamp', unit: 'day', binSize: 1 } } },
             close: { '$last': '$close' },
             open: { '$first': '$open' },
             high: { '$max': '$high' },
             low: { '$min': '$low' } } },
        { '$project': 
           { timestamp: '$_id.timestamp',
             symbol: '$_id.symbol',
             open: 1,
             close: 1,
             high: 1,
             low: 1,
             _id: 0 } },
        { '$setWindowFields': 
           { partitionBy: '$symbol',
             sortBy: { timestamp: 1 },
             output: 
              { AvgPrice50: { '$avg': '$close', window: { range: [ -50, 0 ], unit: 'day' } },
                AvgPrice200: 
                 { '$avg': '$close',
                   window: { range: [ -200, 0 ], unit: 'day' } } } } },
        { '$match': { timestamp: { '$gte': 2020-01-01T00:00:00.000Z } } } ],
     cursor: {},
     collation: { locale: 'simple' } },
  ok: 1,
  '$clusterTime': 
   { clusterTime: Timestamp({ t: 1641832064, i: 1 }),
     signature: 
      { hash: Binary(Buffer.from("a31fa5b95656466fc6d3965148c09ad8adef4431", "hex"), 0),
        keyId: 7029302708251132000 } },
  operationTime: Timestamp({ t: 1641832064, i: 1 }) }