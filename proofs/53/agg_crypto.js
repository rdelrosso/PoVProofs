[{$group: {
  _id: {
    symbol: "$metadata.symbol",
    timestamp: {
      "$dateTrunc": {
        "date": "$timestamp",
        "unit": "day",
        "binSize": 1
      }
    }
  },
  close: {
    $last: "$close"
  },
  open: {
    $first: "$open"
  },
  high: {
    $max: "$high"
  },
  low: {
    $min: "$low"
  }
}}, {$project: {
  timestamp: "$_id.timestamp",
  symbol: "$_id.symbol",
  open: 1,
  close: 1,
  high: 1,
  low: 1,
  _id: 0
}}, {$setWindowFields: {
  partitionBy: "$symbol",
  sortBy: {
    "timestamp": 1
  },
  output: {
    "AvgPrice50": {
      $avg: "$close",
      window: {
        range: [-50, 0],
        unit: "day"
      }
    },
    "AvgPrice200": {
      $avg: "$close",
      window: {
        range: [-200, 0],
        unit: "day"
      }
    }
  }
}}, {$match: {
  timestamp: {
    $gte: ISODate('2020-01-01T00:00:00.000+00:00')
  }
}}]