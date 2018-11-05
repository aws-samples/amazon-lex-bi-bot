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

ORIGINAL_VALUE = 0
TOP_RESOLUTION = 1

SLOT_CONFIG = {
    'event_name':       {'type': TOP_RESOLUTION, 'remember': True,  'error': 'I couldn\'t find an event called "{}".'},
    'event_month':      {'type': ORIGINAL_VALUE, 'remember': True},
    'venue_name':       {'type': ORIGINAL_VALUE, 'remember': True},
    'venue_city':       {'type': ORIGINAL_VALUE, 'remember': True},
    'venue_state':      {'type': ORIGINAL_VALUE, 'remember': True},
    'cat_desc':         {'type': TOP_RESOLUTION, 'remember': True,  'error': 'I couldn\'t find a category called "{}".'},
    'count':            {'type': ORIGINAL_VALUE, 'remember': True},
    'dimension':        {'type': ORIGINAL_VALUE, 'remember': True},
    'one_event':        {'type': TOP_RESOLUTION, 'remember': False, 'error': 'I couldn\'t find an event called "{}".'},
    'another_event':    {'type': TOP_RESOLUTION, 'remember': False, 'error': 'I couldn\'t find an event called "{}".'},
    'one_venue':        {'type': ORIGINAL_VALUE, 'remember': False},
    'another_venue':    {'type': ORIGINAL_VALUE, 'remember': False},
    'one_month':        {'type': ORIGINAL_VALUE, 'remember': False},
    'another_month':    {'type': ORIGINAL_VALUE, 'remember': False},
    'one_city':         {'type': ORIGINAL_VALUE, 'remember': False},
    'another_city':     {'type': ORIGINAL_VALUE, 'remember': False},
    'one_state':        {'type': ORIGINAL_VALUE, 'remember': False},
    'another_state':    {'type': ORIGINAL_VALUE, 'remember': False},
    'one_category':     {'type': TOP_RESOLUTION, 'remember': False,  'error': 'I couldn\'t find a category called "{}".'},
    'another_category': {'type': TOP_RESOLUTION, 'remember': False,  'error': 'I couldn\'t find a category called "{}".'}
}

DIMENSIONS = {
    'events':     {'slot': 'event_name',  'column': 'e.event_name',  'singular': 'event'},
    'months':     {'slot': 'event_month', 'column': 'd.month',       'singular': 'month'},
    'venues':     {'slot': 'venue_name',  'column': 'v.venue_name',  'singular': 'venue'},
    'cities':     {'slot': 'venue_city',  'column': 'v.venue_city',  'singular': 'city'},
    'states':     {'slot': 'venue_state', 'column': 'v.venue_state', 'singular': 'state'},
    'categories': {'slot': 'cat_desc',    'column': 'c.cat_desc',    'singular': 'category'}
}


class SlotError(Exception):
    pass

