#!/bin/bash

#
# Builds the bot, intents, and custom slot types
#

#
# Environment variables to be set in the CodeBuild project
#
# $BOT				Name of the Lex bot
# $INTENTS      		List of intent names for the bot
# $SLOTS        		List of slot type names for the bot
# $LAMBDA       		Name of the Lambda fulfillment function for the bot
# $LAMBDA_ROLE_ARN     		ARN for the Lambda execution role
# $ATHENA_DB    		Name of the Athena database
# $ATHENA_OUTPUT_LOCATION	Name of the S3 bucket for Athena output
#

# Load the Lambda functions for each Intent
echo "Lambda execution role = $LAMBDA_ROLE_ARN"
for i in $INTENTS
do
    module_name=`echo $i | tr '[:upper:]' '[:lower:]'`
    echo "Creating Lambda handler function: ${LAMBDA}_${i} from ${module_name}.py"
    # echo aws lambda create-function \
    #     --function-name ${LAMBDA}_${i} \
    #     --description "${LAMBDA} ${i} Intent Handler" \
    #     --timeout 300 \
    #     --zip-file fileb://${i}.zip \
    #     --role $LAMBDA_ROLE_ARN \
    #     --handler ${module_name}.lambda_handler \
    #     --runtime python3.9 \
    #     --environment "Variables={ATHENA_DB=$ATHENA_DB,ATHENA_OUTPUT_LOCATION=$ATHENA_OUTPUT_LOCATION}" 

    aws lambda create-function \
        --function-name ${LAMBDA}_${i} \
        --description "${LAMBDA} ${i} Intent Handler" \
        --timeout 300 \
        --zip-file fileb://${i}.zip \
        --role $LAMBDA_ROLE_ARN \
        --handler ${module_name}.lambda_handler \
        --runtime python3.9 \
	--environment "Variables={ATHENA_DB=$ATHENA_DB,ATHENA_OUTPUT_LOCATION=$ATHENA_OUTPUT_LOCATION}" \
        >/dev/null

    # echo "Adding permission to invoke Lambda handler function ${LAMBDA}_${i} from Amazon Lex"
    # echo aws lambda add-permission \
    #     --function-name ${LAMBDA}_${i} \
    #     --statement-id chatbot-fulfillment \
    #     --action "lambda:InvokeFunction" \
    #     --principal "lex.amazonaws.com" 

    aws lambda add-permission \
        --function-name ${LAMBDA}_${i} \
        --statement-id chatbot-fulfillment \
        --action "lambda:InvokeFunction" \
        --principal "lex.amazonaws.com" \
        >/dev/null

    echo; echo; echo
done

for i in $SLOTS
do
	echo "Creating slot type: $i"
	aws lex-models put-slot-type --name $i --cli-input-json file://slots/$i.json >/dev/null 
done

# build the intents
for i in $INTENTS
do
	echo "Creating intent: $i"
        # substitute the ARN for the Lambda intent handler function

        LAMBDA_ARN=`aws lambda get-function --function-name ${LAMBDA}_${i} | grep 'FunctionArn' | sed 's/.*FunctionArn": "\(.*\)".*/\1/'`

        sed "s/{{lambda-arn}}/$LAMBDA_ARN/" intents/$i.json >intents/$i-updated.json
        # echo "ARN for $i = `grep -i arn intents/$i-updated.json`"
	aws lex-models put-intent --name $i --cli-input-json file://intents/$i-updated.json >/dev/null 
done

# build the bot 
echo "Creating bot: $BOT"
if aws lex-models put-bot --name $BOT --cli-input-json file://bots/$BOT.json >/dev/null
then echo "Success: $BOT bot build complete."; exit 0
else echo "Error: $BOT bot build failed, check the log for errors"; exit 1
fi


