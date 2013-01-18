#!/usr/bin/python
import calendar
from datetime import datetime
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('config.ini')
 
WEEKDAY_BUDGET = int(parser.get('budget', 'week_day'))
WEEKEND_BUDGET = int(parser.get('budget', 'weekend_day'))

FIXED_SPENDINGS = {}
for name, value in parser.items('expenses'):
    day, amount = value.split(':')
    FIXED_SPENDINGS[int(day)] = int(amount)

MON, TUE, WED, THU, FRI, SAT, SUN = range(7)

now = datetime.now()
cal = calendar.Calendar()

def is_weekday(i): 
    return MON <= i <= FRI

midmonth_payday = 0
endmonth_payday = 0
iter = cal.itermonthdays2(now.year, now.month)
for dom, dow in iter:
    if dom == 0: 
        continue
    if is_weekday(dow): 
        last_weekday = dom
    if dom == 15: 
        midmonth_payday = last_weekday
endmonth_payday = last_weekday

days_until_pay = 0
if now.day < midmonth_payday:
    days_until_pay = midmonth_payday - now.day
else:
    days_until_pay = endmonth_payday - now.day

estimated_spending = 0
iter = cal.itermonthdays2(now.year, now.month)
for dom, dow in iter:
    if dom < now.day:
        continue

    if dom in FIXED_SPENDINGS: 
        estimated_spending += FIXED_SPENDINGS[dom]

    if is_weekday(dow):
        estimated_spending += WEEKDAY_BUDGET
    else:
        estimated_spending += WEEKEND_BUDGET
    
    if dom == (midmonth_payday - 1): 
        break
    if dom == (endmonth_payday - 1):
        break
