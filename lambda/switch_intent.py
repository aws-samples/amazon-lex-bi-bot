#
# Copyright 2017-2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
# http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the
# License for the specific language governing permissions and limitations under the License.

import time
import logging
import json
import bibot_helpers as helpers
import bibot_userexits as userexits
import count_intent
import top_intent

#
# See additional configuration parameters at bottom 
#

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
        return switch_intent_handler(event, session_attributes)


def switch_intent_handler(intent_request, session_attributes):
    session_attributes['greetingCount'] = '0'
    session_attributes['resetCount'] = '0'
    session_attributes['finishedCount'] = '0'
    # note: do not alter session_attributes['lastIntent'] here

    if session_attributes.get('lastIntent', None) is not None:
        intent_name = session_attributes['lastIntent']
        if INTENT_CONFIG.get(intent_name, False):
            logger.debug('<<BIBot>> switch_intent_handler: session_attributes = ' + json.dumps(session_attributes))
            logger.debug('<<BIBot>> switch_intent_handler: refirecting to ' + intent_name)
            return INTENT_CONFIG[intent_name]['handler'](intent_request, session_attributes)    # dispatch to the event handler
        else:
            return helpers.close(session_attributes, 'Fulfilled',
                {'contentType': 'PlainText', 'content': 'Sorry, I don\'t support the intent called "' + intent_name + '".'})
    else:
        return helpers.close(session_attributes, 'Fulfilled',
            {'contentType': 'PlainText', 'content': 'Sorry, I\'m not sure what you\'re asking me.'})


INTENT_CONFIG = {
    'Top_Intent':       {'handler': top_intent.top_intent_handler},
    'Count_Intent':     {'handler': count_intent.count_intent_handler}
}

