#!/bin/bash

ENV_FILE_NAME=".mongorc-env.js"
FULL_PATH_TARGET="$HOME/$ENV_FILE_NAME"
RC_COMMAND="load(\"$FULL_PATH_TARGET\")"
MONGO_RC_FILE="$HOME/.mongorc.js"
ALPHA_USER=$(echo $USER | sed s/[^a-zA-Z0-9]//g)

# 
# See of the .mongorc-env.js aleady exists in the user's HOME directory
# 
if [[ -f $FULL_PATH_TARGET ]]
then
    #
    # Do Nothing if it exists
    #
    echo "$FULL_PATH_TARGET already Exists -- NO CHANGES MADE"
else
    #
    # Create if it doesn't exist
    #
    echo "Creating $FULL_PATH_TARGET..."
cat >$FULL_PATH_TARGET <<EOF
env = {}
env.USER = "$ALPHA_USER"
EOF
fi
#
# See if we are already loading the .mongorc-env.js file in ./mongorc.js
#
if [ ! -z $(grep "$RC_COMMAND" "$MONGO_RC_FILE") ]
then
    #
    # Already being loaded - do nothing
    #
    echo "$MONGO_RC_FILE is already loading $FULL_PATH_TARGET -- No Changes Made"
else
    #
    # Add the load command to ~/.mongorc.js
    #
    echo $RC_COMMAND >> $MONGO_RC_FILE
fi