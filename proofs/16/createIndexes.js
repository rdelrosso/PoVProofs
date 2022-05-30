db = db.getSiblingDB("airlines");
db.on_time_perf.createIndex({"Origin.Origin":1});
db.on_time_perf.createIndex({"UniqueCarrier":1});
db.on_time_perf.createIndex({"Carrier":1});
db.on_time_perf.createIndex({"Origin.State":1});
db.on_time_perf.createIndex({"Origin.CityName":1});
db.on_time_perf.createIndex({"Month":1});
db.on_time_perf.createIndex({"DayOfMonth":1});
