#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import boto3
import time
import logging
import json
import pprint
import bibot_helpers as helpers
import bibot_userexits as userexits

#
# parameters for Refresh intent
#
REFRESH_QUERY = 'SELECT DISTINCT event_name from event ORDER BY event_name'
REFRESH_SLOT = 'event_name'
REFRESH_INTENT = 'Compare_Intent'
REFRESH_BOT = 'BIBot'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    logger.debug('<<BIBot>> Lex event info = ' + json.dumps(event))

    session_attributes = event['sessionAttributes']
    logger.debug('<<BIBot>> lambda_handler: session_attributes = ' + json.dumps(session_attributes))

    config_error = helpers.get_bibot_config()
    if config_error is not None:
        return helpers.close(session_attributes, 'Fulfilled',
            {'contentType': 'PlainText', 'content': config_error})   
    else:
        return refresh_intent_handler(event, session_attributes)


def refresh_intent_handler(intent_request, session_attributes):
    athena = boto3.client('athena')
    session_attributes['lastIntent'] = None

    # Build and execute query
    logger.debug('<<BIBot>> Athena Query String = ' + REFRESH_QUERY)            

    st_values = []
    response = helpers.execute_athena_query(REFRESH_QUERY)
    logger.debug('<<BIBot>> query response = ' + json.dumps(response)) 

    while len(response['ResultSet']['Rows']) > 0:
        for item in response['ResultSet']['Rows']:
            st_values.append({'value': item['Data'][0]['VarCharValue']})
            logger.debug('<<BIBot>> appending: ' + item['Data'][0]['VarCharValue']) 
        
        try:
            next_token = response['NextToken']
            response = athena.get_query_results(QueryExecutionId=query_execution_id, NextToken=next_token, MaxResults=100)
            logger.debug('<<BIBot>> additional query response = ' + json.dumps(response)) 
        except KeyError:
            break

    logger.debug('<<BIBot>> "st_values = ' + pprint.pformat(st_values)) 
        
    lex_models = boto3.client('lex-models')
    response = lex_models.get_slot_type(name=REFRESH_SLOT, version='$LATEST')
    logger.debug('<<BIBot>> "boto3 version = ' + boto3.__version__) 
    logger.debug('<<BIBot>> "Lex slot event_name = ' + pprint.pformat(response, indent=4)) 
    logger.debug('<<BIBot>> "Lex slot event_name checksum = ' + response['checksum']) 
    logger.debug('<<BIBot>> "Lex slot event_name valueSelectionStrategy = ' + response['valueSelectionStrategy']) 
    
    try:
        logger.debug('<<BIBot>> "st_values = ' + pprint.pformat(st_values)) 

        st_checksum = response['checksum']
        response = lex_models.put_slot_type(name=response['name'],
                                            description=response['description'],
                                            enumerationValues=st_values,
                                            checksum=response['checksum'],
                                            valueSelectionStrategy=response['valueSelectionStrategy']
                                            )
    except KeyError:
        pass
    
    response = lex_models.get_intent(name=REFRESH_INTENT, version='$LATEST')
    logger.debug('<<BIBot>> Lex get-intent = ' + pprint.pformat(response, indent=4)) 
    logger.debug('<<BIBot>> Lex get-intent keys = ' + pprint.pformat(response.keys()))
    
    response = lex_models.put_intent(name=response['name'],
                                     description=response['description'],
                                     slots=response['slots'],
                                     sampleUtterances=response['sampleUtterances'],
                                     conclusionStatement=response['conclusionStatement'],
                                     fulfillmentActivity=response['fulfillmentActivity'],
                                     checksum=response['checksum']
                                    )
    
    response = lex_models.get_bot(name=REFRESH_BOT, versionOrAlias='$LATEST')
    logger.debug('<<BIBot>> Lex bot = ' + pprint.pformat(response, indent=4)) 
    
    response = lex_models.put_bot(name=REFRESH_BOT,
                                  description=response['description'],
                                  intents=response['intents'],
                                  clarificationPrompt=response['clarificationPrompt'],
                                  abortStatement=response['abortStatement'],
                                  idleSessionTTLInSeconds=response['idleSessionTTLInSeconds'],
                                  voiceId=response['voiceId'],
                                  processBehavior='SAVE',
                                  locale=response['locale'],
                                  checksum=response['checksum'],
                                  childDirected=response['childDirected']
                                 )

    logger.debug('<<BIBot>> Lex put bot = ' + pprint.pformat(response, indent=4)) 

    response_string = "I've refreshed the events dimension from the database.  Please rebuild me."
    return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})   

