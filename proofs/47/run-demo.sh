#!/bin/bash

##
## wrapper for query-api.sh, simplifies authentication
##

# Set POV_APP_ID here if your demo environment is durable
POV_APP_ID=

# Test for 'jq' (rarely installed by default)
if [ $(echo '[]' | jq '1') -ne 1 ]; then
    echo Please install \'jq\' to use this script
fi

# Test that POV_APP_ID is set
if [ -z $POV_APP_ID ] && [ -z $1 ]; then
    echo "USAGE: $0 [REALM APP ID]"
    exit
elif [ $1 ]; then
    echo "Setting POV_APP_ID to $1"
    POV_APP_ID=$1
else
    echo "Using default POV_APP_ID of $POV_APP_ID"
fi

# Function returns access_token from realm logon
# (Results of logon are passed through a jq filter and echoed)
do-anon-login () {
    echo $(curl --silent -X POST "https://stitch.mongodb.com/api/client/v2.0/app/$1/auth/providers/anon-user/login" | jq '.["access_token"]' | tr -d '"')
}

# Call the funtion with POV_APP_ID as arg
RESULT=$(do-anon-login $POV_APP_ID)

# Test that result is a non-empty string
if [ -z TOKEN ]; then
    echo "Error in logon function"
fi

# Set results in env and call the demo script
export POV_APP_ID=$POV_APP_ID
export POV_ACCESS_TOKEN=$RESULT
./query-api.sh
