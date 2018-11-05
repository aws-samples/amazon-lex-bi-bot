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

import logging
import json
import jasper_config as jasper
import jasper_helpers as helpers
import jasper_userexits as userexits

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    logger.debug('<<Jasper>> Lex event info = ' + json.dumps(event))

    session_attributes = event['sessionAttributes']
    logger.debug('<<Jasper>> lambda_handler: session_attributes = ' + json.dumps(session_attributes))

    config_error = helpers.get_jasper_config()
    if config_error is not None:
        return helpers.close(session_attributes, 'Fulfilled',
            {'contentType': 'PlainText', 'content': config_error})   
    else:
        return goodbye_intent_handler(event, session_attributes)


def goodbye_intent_handler(intent_request, session_attributes):
    session_attributes['greetingCount'] = '0'
    session_attributes['resetCount'] = '0'
    session_attributes['queryAttributes'] = None
    session_attributes['lastIntent'] = None

    askCount = helpers.increment_counter(session_attributes, 'finishedCount')

    # build response string
    if askCount == 1: response_string = 'Nice chatting with you.  Talk to you later!'
    elif askCount == 2: response_string = 'Bye now!'
    elif askCount == 3: response_string = 'Hope I was able to help!'
    elif askCount == 4: response_string = 'See ya!'
    elif askCount == 5: response_string = 'Really?'
    else: response_string = 'Ok'

    slot_values = {key: None for key in jasper.SLOT_CONFIG}
    helpers.remember_slot_values(slot_values, session_attributes)

    return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})   

