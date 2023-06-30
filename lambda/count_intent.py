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

import time
import logging
import json
import bibot_config as bibot
import bibot_helpers as helpers
import bibot_userexits as userexits

# SELECT statement for Count query


COUNT_SELECT = "SELECT SUM(ie.revenue) FROM invoice_events ie "
COUNT_JOIN = " "
COUNT_WHERE = " WHERE {} = '{}' AND {} = '{}' AND {} = '{}'"   
COUNT_PHRASE = 'Dollars generated'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    logger.debug('<<BIBot>> Lex event info = ' + json.dumps(event))

    config_error = helpers.get_bibot_config()

    session_attributes = event['sessionAttributes']
    logger.debug('<<BIBot>> lambda_handler: session_attributes = ' + json.dumps(session_attributes))

    if config_error is not None:
        return helpers.close(session_attributes, 'Fulfilled',
            {'contentType': 'PlainText', 'content': config_error})   
    else:
        return count_intent_handler(event, session_attributes)


def count_intent_handler(intent_request, session_attributes):
    method_start = time.perf_counter()
    
    logger.debug('<<BIBot>> count_intent_handler: intent_request = ' + json.dumps(intent_request))
    logger.debug('<<BIBot>> count_intent_handler: session_attributes = ' + json.dumps(session_attributes))
    
    session_attributes['greetingCount'] = '1'
    session_attributes['resetCount'] = '0'
    session_attributes['finishedCount'] = '0'
    session_attributes['lastIntent'] = 'Count_Intent'

    # Retrieve slot values from the current request
    slot_values = session_attributes.get('slot_values')

    try:
        slot_values = helpers.get_slot_values(slot_values, intent_request)
    except bibot.SlotError as err:
        return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': str(err)})   
    
    logger.debug('<<BIBot>> "count_intent_handler(): slot_values: %s', slot_values)

    # Retrieve "remembered" slot values from session attributes
    slot_values = helpers.get_remembered_slot_values(slot_values, session_attributes)
    logger.debug('<<BIBot>> "count_intent_handler(): slot_values afer get_remembered_slot_values: %s', slot_values)

    # Remember updated slot values
    helpers.remember_slot_values(slot_values, session_attributes)
    
    # build and execute query
    select_clause = COUNT_SELECT
    where_clause = COUNT_JOIN

    slot_key = 'event_date'
    year, month, day = userexits.pre_process_query_value(slot_key, slot_values[slot_key])
    
    where_clause += COUNT_WHERE.format('year', year, 'month', month, 'day', day)

    query_string = select_clause + where_clause
    
    response = helpers.execute_athena_query(query_string)

    result = response['ResultSet']['Rows'][1]['Data'][0]
    if result:
        count = result['VarCharValue']
    else:
        count = 0

    logger.debug('<<BIBot>> "Count value is: %s' % count) 

    # build response string
    if count == 0:
        response_string = 'There was no revenue generated'.format(COUNT_PHRASE)
    else:
        response_string = 'There were {} {}'.format(count, COUNT_PHRASE)

    response_string += ' in {}'.format(slot_values[slot_key])

    return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})   
