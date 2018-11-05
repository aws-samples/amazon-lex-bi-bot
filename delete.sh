#!/bin/bash

#
# Deletes the bot, intents, and custom slot types
# in reverse order of build: first the bot, then
# the intents, then the slot types.
#

#
# Environment variables to be set in the CodeBuild project
#
# $BOT		Name of the Lex bot
# $INTENTS      List of intent names for the bot
# $SLOTS        List of slot type names for the bot
# $LAMBDA       Name of the Lambda fulfillment function for the bot
#

SLEEP=2

# Delete TICKIT database if it exists
if aws glue get-database --name $ATHENA_DB >xxx 2>&1
then 
	echo "Deleting Athena database $ATHENA_DB"
	aws glue delete-database --name $ATHENA_DB >/dev/null
fi

# delete the bot if it exists
echo -n "Checking for existing bot $BOT... " 
if aws lex-models get-bot --name $BOT --version-or-alias '$LATEST' >/dev/null 2>&1
then 
    echo "deleting"
    sleep $SLEEP
    aws lex-models delete-bot --name $BOT
    sleep $SLEEP
else
    echo "not found."
fi

# delete the intents
for i in $INTENTS
do
    echo -n "Checking for existing intent $i... "
    if aws lex-models get-intent --name $i --intent-version '$LATEST' >/dev/null 2>&1
    then 
        echo "deleting"
        sleep $SLEEP
        aws lex-models delete-intent --name $i
        sleep $SLEEP
    else
        echo "not found"
    fi
done

# delete the custom slot types
for i in $SLOTS
do
    echo -n "Checking for existing slot type $i... "
    if aws lex-models get-slot-type --name $i --slot-type-version '$LATEST' >/dev/null 2>&1
    then 
        echo "deleting"
        sleep $SLEEP
        aws lex-models delete-slot-type --name $i
        sleep $SLEEP
    else
        echo "not found"
    fi
done
 
# delete the lambda functions
for i in $INTENTS
do
    echo -n "Checking for existing Lambda function ${LAMBDA}_${i}... "
    if aws lambda get-function --function-name ${LAMBDA}_${i} >/dev/null 2>&1
    then 
        echo "deleting"
        sleep $SLEEP
        aws lambda delete-function --function-name ${LAMBDA}_${i}
        sleep $SLEEP
    else
        echo "not found"
    fi
done

