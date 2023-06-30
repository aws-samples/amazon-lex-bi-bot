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
    # custom slot : TOP_res
    'event_namespace': {'type': TOP_RESOLUTION, 'remember': True,  'error': 'I couldn\'t find an namespace called "{}".'},
    'event_type': {'type': TOP_RESOLUTION, 'remember': True,  'error': 'I couldn\'t find a type called "{}".'},
    'event_invoice': {'type': TOP_RESOLUTION, 'remember': True,  'error': 'I couldn\'t find an invoice called "{}".'},
    'event_account': {'type': TOP_RESOLUTION, 'remember': True,  'error': 'I couldn\'t find an account called "{}".'},
    'event_revenue': {'type': TOP_RESOLUTION, 'remember': True,  'error': 'I couldn\'t find a revenue called "{}".'},
    'event_bill': {'type': TOP_RESOLUTION, 'remember': True,  'error': 'I couldn\'t find a bill called "{}".'},
    'event_year': {'type': ORIGINAL_VALUE, 'remember': True},
    'event_month': {'type': ORIGINAL_VALUE, 'remember': True},
    'event_day': {'type': ORIGINAL_VALUE, 'remember': True},
    'event_date': {'type': ORIGINAL_VALUE, 'remember': True},
    'count': {'type': ORIGINAL_VALUE, 'remember': True},
    'dimension': {'type': ORIGINAL_VALUE, 'remember': True},
}

DIMENSIONS = {
    'namespaces': {'slot': 'event_namespace', 'column': 'ie.namespace', 'singular': 'namespace'},
    'types': {'slot': 'event_type', 'column': 'ie.type', 'singular': 'type'},
    'invoices': {'slot': 'event_invoice', 'column': 'ie.invoice', 'singular': 'invoice'},
    'accounts': {'slot': 'event_account', 'column': 'ie.account', 'singular': 'account'},
    'bills': {'slot': 'event_bill', 'column': 'ie.bill', 'singular': 'bill'},
    'revenue': {'slot': 'event_revenue', 'column': 'ie.column', 'singular': 'revenue'},
    'years': {'slot': 'event_year', 'column': 'ie.year', 'singular': 'year'},
    'months': {'slot': 'event_month', 'column': 'ie.month', 'singular': 'month'},
    'days': {'slot': 'event_day', 'column': 'ie.day', 'singular': 'day'}
}



# producer, namespace, type, invoice, account, bill, revenue, year, month, day

# How many "accounts" are {skip}.

# How many {Namespace - Invoicing.prod} are there on Jan1 - Namespace: ->  
# How many {Namespace - FDR.prod} are there on Jan1 - Namespace: -> 

# What is the {revenue} for {dimension}-{slot}
# What is the revenue for invoice-{01238021938} - SLOT
# What is the revenue for account-{01238021938} - SLOT

# Column - Dimension, Row - Slot

# Example of a question with column/row
# 


class SlotError(Exception):
    pass

