#!/usr/bin/python
import sys
import logging
from datetime import datetime

import chase
from budget import days_until_pay, estimated_spending
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('config.ini')
 
check_avail = chase.get_checking()

date = datetime.now().isoformat()
date = date[:19] # cut off microseconds

check_avail = int(check_avail.replace(",", ""))
check_leftover = check_avail - estimated_spending

activity = chase.get_activity()

last_activity = chase.get_activity()[0].lower()

output = "%s\n\n%d %d days %d [ %d ]" % (last_activity,
        check_avail, days_until_pay, estimated_spending, check_leftover)

f = open('last', 'r')
last = int(f.readline())
f.close()

now = datetime.now()
if check_avail != last:
    from twilio.rest import TwilioRestClient
    account = parser.get('twilio', 'account')
    token = parser.get('twilio', 'token')
    client = TwilioRestClient(account, token)
    target_number = parser.get('twilio', 'target_number')
    number = parser.get('twilio', 'number')
    message = client.sms.messages.create(to=target_number, from_=number, body=output)
    print(str(now) + ' - SMS sent')
else:
    print(str(now) + ' - not changed')

f = open('last', 'w')
f.write(str(check_avail))
f.close()

