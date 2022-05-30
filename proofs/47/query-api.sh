if [ -z "$POV_APP_ID" ] || [ -z "$POV_ACCESS_TOKEN" ];
then
  echo "Variable(s) POV_APP_ID and/or POV_ACCESS_TOKEN are not defined. Please run export VARIABLE=VALUE before running this script."
else
  for i in {1..10};
  do curl -X POST "https://stitch.mongodb.com/api/client/v2.0/app/${POV_APP_ID}/graphql" \
    -H "Authorization: Bearer ${POV_ACCESS_TOKEN}" \
    -H 'Content-Type: application/json' \
    -d '{"query":"{ movies(query: {year: 1942}) { title\n year\n runtime\n plot}}"}' -s -o response-graphql.json -w "%{response_code}: GraphQL query took %{time_total} seconds. Downloaded %{size_download} bytes\n"
  done

  for i in {1..10};
  do curl "https://stitch.mongodb.com/api/client/v2.0/app/${POV_APP_ID}/functions/call" \
    -H "Authorization: Bearer ${POV_ACCESS_TOKEN}" \
    -H 'content-type: application/json' \
    -d '{"name":"find","service":"mongodb-atlas","arguments":[{"collection":"movies","database":"sample_mflix","query":{"year": 1942},"sort":{}}]}' -s -o response-stitch-rules.json -w "%{response_code}: Stitch Rules query took %{time_total} seconds. Downloaded %{size_download} bytes\n"
  done
fi