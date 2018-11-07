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

COMPARE_CONFIG = {
    'events':     {'1st': 'one_event',    '2nd': 'another_event',    'error': 'Sorry, try "Compare sales for Event 1 versus Event 2'},
    'months':     {'1st': 'one_month',    '2nd': 'another_month',    'error': 'Sorry, try "Compare sales for Month 1 versus Month 2'},
    'venues':     {'1st': 'one_venue',    '2nd': 'another_venue',    'error': 'Sorry, try "Compare sales for Venue 1 versus Venue 2'},
    'cities':     {'1st': 'one_city',     '2nd': 'another_city',     'error': 'Sorry, try "Compare sales for City 1 versus City 2'},
    'states':     {'1st': 'one_state',    '2nd': 'another_state',    'error': 'Sorry, try "Compare sales for State 1 versus State 2'},
    'categories': {'1st': 'one_category', '2nd': 'another_category', 'error': 'Sorry, try "Compare sales for Category 1 versus Category 2'}
}

# SELECT statement for Compare query
COMPARE_SELECT = "SELECT {}, SUM(s.amount) ticket_sales  FROM sales s, event e, venue v, category c, date_dim d "
COMPARE_JOIN = " WHERE e.event_id = s.event_id AND v.venue_id = e.venue_id AND c.cat_id = e.cat_id AND d.date_id = e.date_id "
COMPARE_WHERE = " AND LOWER({}) LIKE LOWER('%{}%') "  
COMPARE_ORDERBY = " GROUP BY {} ORDER BY ticket_sales DESC "

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
        return compare_intent_handler(event, session_attributes)


def compare_intent_handler(intent_request, session_attributes):
    method_start = time.perf_counter()
    
    logger.debug('<<BIBot>> compare_intent_handler: session_attributes = ' + json.dumps(session_attributes))

    session_attributes['greetingCount'] = '1'
    session_attributes['resetCount'] = '0'
    session_attributes['finishedCount'] = '0'
    session_attributes['lastIntent'] = None    # "switch" handling done in Compare_Intent

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
    
    for key,config in COMPARE_CONFIG.items():
        if slot_values.get(config['1st']):
            if slot_values.get(config['2nd']) is None:
                return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText', 'content': config['error'] })
            
            slot_values['dimension'] = key
            slot_values[bibot.DIMENSIONS[key]['slot']] = None
            
            the_1st_dimension_value = slot_values[config['1st']].lower()
            the_2nd_dimension_value = slot_values[config['2nd']].lower()

            break

    # Build and execute query
    select_clause = COMPARE_SELECT.format(bibot.DIMENSIONS[slot_values['dimension']]['column'])
    where_clause = COMPARE_JOIN

    the_1st_dimension_value = userexits.pre_process_query_value(bibot.DIMENSIONS[key]['slot'], the_1st_dimension_value)
    the_2nd_dimension_value = userexits.pre_process_query_value(bibot.DIMENSIONS[key]['slot'], the_2nd_dimension_value)
    where_clause += "   AND (LOWER(" + bibot.DIMENSIONS[slot_values['dimension']]['column'] + ") LIKE LOWER('%" + the_1st_dimension_value + "%') OR "
    where_clause +=         "LOWER(" + bibot.DIMENSIONS[slot_values['dimension']]['column'] + ") LIKE LOWER('%" + the_2nd_dimension_value + "%')) " 

    logger.debug('<<BIBot>> compare_sales_intent_request - building WHERE clause') 
    for dimension in bibot.DIMENSIONS:
        slot_key = bibot.DIMENSIONS.get(dimension).get('slot')
        if slot_values[slot_key] is not None:
            logger.debug('<<BIBot>> compare_sales_intent_request - calling userexits.pre_process_query_value(%s, %s)', 
                         slot_key, slot_values[slot_key])  
            value = userexits.pre_process_query_value(slot_key, slot_values[slot_key])
            where_clause += COMPARE_WHERE.format(bibot.DIMENSIONS.get(dimension).get('column'), value)

    order_by_group_by = COMPARE_ORDERBY.format(bibot.DIMENSIONS[slot_values['dimension']]['column'])

    query_string = select_clause + where_clause + order_by_group_by
    
    logger.debug('<<BIBot>> Athena Query String = ' + query_string)  
    
    response = helpers.execute_athena_query(query_string)

    # Build response string
    response_string = ''
    result_count = len(response['ResultSet']['Rows']) - 1

    # add the English versions of the WHERE clauses
    counter = 0
    for dimension in bibot.DIMENSIONS:
        slot_key = bibot.DIMENSIONS[dimension].get('slot')
        logger.debug('<<BIBot>> pre compare_sale_formatter[%s] = %s', slot_key, slot_values.get(slot_key))
        if slot_values.get(slot_key) is not None:
            # the DIMENSION_FORMATTERS perform a post-process function and then format the output
            # Example:  {... 'venue_state': {'format': ' in the state of {}',  'function': get_state_name}, ...}
            if userexits.DIMENSION_FORMATTERS.get(slot_key) is not None:
                output_text = userexits.DIMENSION_FORMATTERS[slot_key]['function'](slot_values.get(slot_key))
                if counter == 0:
                    response_string += userexits.DIMENSION_FORMATTERS[slot_key]['format'].format(output_text)
                else:
                    response_string += ', ' + userexits.DIMENSION_FORMATTERS[slot_key]['format'].lower().format(output_text)
                counter += 1
                logger.debug('<<BIBot>> compare_sales_formatter[%s] = %s', slot_key, output_text)

    if (result_count == 0):
        if len(response_string) > 0:
            response_string += ', '
        response_string += "I didn't find any results for the " + slot_values['dimension']
        response_string += " " + userexits.post_process_dimension_output(key, the_1st_dimension_value)
        response_string += " and " + userexits.post_process_dimension_output(key, the_2nd_dimension_value) + "."

    elif (result_count == 1):
        if len(response_string) > 0:
            response_string += ', there '
        else:
            response_string += 'There '
        response_string += 'is only one ' + bibot.DIMENSIONS[slot_values['dimension']]['singular'] + '.'
        
    elif (result_count == 2):
        # put the results into a dict for easier reference by name
        result_set = {}
        result_set.update( { response['ResultSet']['Rows'][1]['Data'][0]['VarCharValue'].lower() : [
                             response['ResultSet']['Rows'][1]['Data'][0]['VarCharValue'],  
                             float(response['ResultSet']['Rows'][1]['Data'][1]['VarCharValue']) ] } )
        result_set.update( { response['ResultSet']['Rows'][2]['Data'][0]['VarCharValue'].lower() : [
                             response['ResultSet']['Rows'][2]['Data'][0]['VarCharValue'],  
                             float(response['ResultSet']['Rows'][2]['Data'][1]['VarCharValue']) ] } )

        logger.debug('<<BIBot>> compare_intent_handler - result_set = %s', result_set) 

        the_1st_dimension_string = result_set[the_1st_dimension_value.lower()][0]
        the_1st_dimension_string = userexits.post_process_dimension_output(key, the_1st_dimension_string)
        the_2nd_dimension_string = result_set[the_2nd_dimension_value.lower()][0]
        the_2nd_dimension_string = userexits.post_process_dimension_output(key, the_2nd_dimension_string)

        if len(response_string) == 0:
            response_string = 'Sales for ' + the_1st_dimension_string + ' were '
        else:
            response_string += ', sales for ' + the_1st_dimension_string + ' were '

        the_1st_amount = result_set[the_1st_dimension_value.lower()][1]
        the_2nd_amount = result_set[the_2nd_dimension_value.lower()][1]
        
        the_1st_amount_formatted = '{:,.0f}'.format(the_1st_amount)
        the_2nd_amount_formatted = '{:,.0f}'.format(the_2nd_amount)
        
        if (the_1st_amount == the_2nd_amount):
            response_string += 'the same as for ' + the_2nd_dimension_string + ', $' + the_2nd_amount_formatted
        else:
            if (the_1st_amount < the_2nd_amount):
                percent_different = (the_1st_amount - the_2nd_amount) / the_2nd_amount * -1
                higher_or_lower = 'lower'
            else:
                percent_different = (the_1st_amount - the_2nd_amount) / the_2nd_amount
                higher_or_lower = 'higher'

            response_string += '{:.0%}'.format(percent_different) + ' ' + higher_or_lower + ' than for ' + the_2nd_dimension_string
            response_string += ': $' + the_1st_amount_formatted + ' as opposed to $' + the_2nd_amount_formatted + '.'

    else:  # >2, should not occur
        response_string = 'I seem to have a problem, I got back ' + str(result_count) + ' ' + dimension + '.'
    
    logger.debug('<<BIBot>> response_string = ' + response_string) 

    method_duration = time.perf_counter() - method_start
    method_duration_string = 'method time = %.0f' % (method_duration * 1000) + ' ms'
    logger.debug('<<BIBot>> "Method duration is: ' + method_duration_string) 

    return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})   

