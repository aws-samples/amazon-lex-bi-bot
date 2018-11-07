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
        return reset_intent_handler(event, session_attributes)


def reset_intent_handler(intent_request, session_attributes):
    session_attributes['greetingCount'] = '1'
    session_attributes['finishedCount'] = '0'
    # don't alter session_attributes['lastIntent'], let BIBot remember the last used intent

    # Retrieve "remembered" slot values from session attributes
    slot_values = helpers.get_remembered_slot_values(None, session_attributes)

    dimensions_reset = ''

    # Retrieve slot values from the current request to see what needs to be reset
    slots_to_reset = helpers.get_slot_values(None, intent_request)

    # check to see if any remembered slots need forgetting
    for key,config in bibot.SLOT_CONFIG.items():
        if key == 'dimension':    # see below
            continue
        if config.get('remember', False):
            if slots_to_reset.get(key):        # asking to reset venue_city: los angeles for example
                if slot_values.get(key):
                    value = userexits.post_process_dimension_output(key, slot_values.get(key))
                    dimensions_reset += ' {}'.format(value.title())
                    logger.debug('<<BIBot>> reset_intent_handler() - forgetting slot %s value %s', key, slot_values[key])
                    slot_values[key] = None
                else:
                    # message = "I wasn't remembering {} - {} anyway.".format(key, slots_to_reset.get(key))
                    message = "I wasn't remembering {} anyway.".format(slots_to_reset.get(key))
                    return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText', 'content': message})

    # check for special case, where the ask is to forget the dimension by name
    dimension = slots_to_reset.get('dimension')
    if dimension and bibot.DIMENSIONS.get(dimension):
        slot_key = bibot.DIMENSIONS[dimension].get('slot')
        if slot_values.get(slot_key):
            logger.debug('<<BIBot>> reset_intent_handler() - forgetting %s (%s)', dimension, slot_values[slot_key])
            value = userexits.post_process_dimension_output(dimension, slot_values[slot_key])
            dimensions_reset += ' {}'.format(value).title()
            logger.debug('<<BIBot>> reset_intent_handler() - forgetting dimension %s slot_key %s value %s', dimension, slot_key, slot_values[slot_key])
            slot_values[slot_key] = None

    if dimensions_reset == '':
        slot_values = {key: None for key in bibot.SLOT_CONFIG}
        dimensions_reset = 'everything'
    
    helpers.remember_slot_values(slot_values, session_attributes)

    response_string = 'OK, I have reset ' + dimensions_reset + '.'

    return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})   

