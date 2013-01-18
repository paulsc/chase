#!/usr/bin/python
import re
import mechanize
from ConfigParser import SafeConfigParser
from HTMLParser import HTMLParser

parser = SafeConfigParser()
parser.read('config.ini')

br = mechanize.Browser(factory=mechanize.RobustFactory())
br.set_handle_robots(False)

#br.set_debug_responses(True)
#br.set_debug_http(True)

br.set_handle_refresh(False)

br.addheaders = [('User-agent', parser.get('auth', 'user_agent'))]

data = None

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def get_data():
    global data
    if data != None:
        return data

    br.open("https://mobilebanking.chase.com/Public/Home/LogOn")

    forms = br.forms()
   
    br.select_form(nr=0)
    br["auth_userId"] = parser.get('auth', 'username')
    br["auth_passwd"] = parser.get('auth', 'password')
    br["LogOn"] = parser.get('auth', 'logon')

    response = br.submit()
    html = response.read()

    regex = re.compile(r"\$([\d,]+)[\.\d]*", re.S)
    moneys = regex.findall(html)

    check_avail = moneys[0]
    check_pres = moneys[1]
    sav_avail = moneys[2]
    sav_pres = moneys[3]
    credit_bal = moneys[4]
    credit_due = moneys[5]
    credit_bal = moneys[6]
    credit_avail = moneys[7]
    credit_total = moneys[8]

    account_id = parser.get('auth', 'account_id')
    br.open("https://mobilebanking.chase.com/Secure/AccountActivity/Index/" + account_id)

    html = br.response().read()

    re_entry = re.compile(r"<tr>(.*)</tr>")
   
    entries = re_entry.findall(html)
    entries = entries[1:] # first entry is bogus
    entries = map(strip_tags, entries) # remove HTML
    entries = list(chunks(entries, 5)) # split in sublists
    
    def remove_unused(array): 
        return [ array[0], array[2] ]

    entries = map(remove_unused, entries)

    def clean_field(field):
        field = field.strip()
        field = ' '.join(field.split())
        field = re.sub('^POS DEBIT ', '', field)
        field = re.sub('^Debit/Credit ', '', field)
        return field

    def clean_entry(entry): 
        tmp = [ clean_field(field) for field in entry ]
        return ' '.join(tmp)

    entries = map(clean_entry, entries)

    data = { 'checking': check_avail, 'savings': sav_avail, 'activity': entries }
    return data

def get_checking(): 
    return get_data()['checking']

def get_savings(): 
    return get_data()['savings']

def get_activity():
    return get_data()['activity']
