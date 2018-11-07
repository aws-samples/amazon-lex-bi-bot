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

