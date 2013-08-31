import datetime
from pymongo import MongoClient
from functools import partial
from itertools import (product, groupby)

def toHumanString(card_name, card_set,
                  buy_data, sell_data):
    arr_str = [card_set, " ", card_name,]
    if not buy_data['then'] == buy_data['now']:
        arr_str.extend([
            ", buy price %05.3f" % (100*buy_data['diff']),
            "%% from %s to %s" % (buy_data['then'], buy_data['now']),
        ])
    if not sell_data['then'] == sell_data['now']:
        arr_str.extend([
            ", sell price %05.3f" % (100*sell_data['diff']),
            "%% from %s to %s" % (sell_data['then'], sell_data['now']),
        ])
    return ''.join(arr_str)

def get_pct_diff(first, second):
    f_first = float(first)
    f_second = float(second)
    if f_first == 0: return 0
    pctdiff = (f_second - f_first) / f_first
    return pctdiff

def reduce_prices(accum, datum, sub_field_name=None):
    key = datum['set_code'] + datum['card_name']
    if key in accum:
        accum[key][sub_field_name] = datum
    else:
        accum[key] = {sub_field_name: datum,
                      'set': datum['set_code']}
    return accum

def get_data(price_type, c_dl, c_prices):
    result = c_dl.find({'type':price_type}).sort([('date', -1)])[0]

    current_date = result['date']
    td = datetime.timedelta(days=1)
    prior_date = current_date - td
    # find recent date closest to 24h ago
    prior_dl = c_dl.find({'date':{'$gte': prior_date},
                          'type':price_type}).sort([('date', 1)])[0]
    prior_date = prior_dl['date']
    # find price data for current and prior dates to compare values
    current_data = c_prices.find({'date': current_date,
                                  'type': price_type}).sort([('set_code', 1),
                                                      ('card_name', 1)])
    prior_data = c_prices.find({'date': prior_date,
                                'type': price_type}).sort([('set_code', 1),
                                                     ('card_name', 1)])
    cur_dict = reduce(partial(reduce_prices, sub_field_name='current'),
                   current_data,
                   {})
    pdict = reduce(partial(reduce_prices, sub_field_name='prior'),
                   prior_data,
                   cur_dict)
    return pdict

def get_report(report_data, sort_field, threshold=.1):
    """
    this sorts positive to negative on sort_field
    """
    # TODO sort the values by set before grouping?
    # TODO re-implement groupby as a dict comp
    sorted_vals = sorted(report_data.itervalues(), key=lambda x: x['set'])
    grouped = groupby(sorted_vals, lambda x: x['set'])
    results = []
    for setcode, values in grouped:
        for value in values:
            # defaults should possibly be set in get_data's reducers instead
            cur = value.get('current', {'buy': 0, 'sell': 0,' qty': {'total': 0}})
            pri = value.get('prior', {'buy': 0, 'sell': 0, 'qty': {'total': 0}})

            # XXX there has to be a better way than doing an extra calc
            field_diff = get_pct_diff(pri.get(sort_field, '0'),
                                      cur.get(sort_field, '0'))
            buydiff = get_pct_diff(pri.get('buy','0'),
                                   cur.get('buy','0'))
            selldiff = get_pct_diff(pri.get('sell','0'),
                                    cur.get('sell','0'))
            if abs(field_diff) > threshold:
                buy_data = {
                    'now': cur.get('buy','0'),
                    'then': pri.get('buy', '0'),
                    'diff': buydiff,
                }
                sell_data = {
                    'now': cur.get('sell', '0'),
                    'then': pri.get('sell', '0'),
                    'diff': selldiff,
                }
                printme = toHumanString(cur['card_name'], cur['set_code'],
                                        buy_data, sell_data)
                results.append({
                    'vals': value,
                    'toString': printme,
                    'sort_val': field_diff
                })
    return {'data': sorted(results, key=lambda x: x['sort_val'], reverse=True), 'sort': sort_field}

def get_report_filename(report):
    return ''.join(['itch_', report['type'], '_', report['sort'], '.txt'])

# XXX percentages still derp
# TODO for an empty report this will probably explode; most likely the 'packs' report
def prepare_report_files(report):
    cur_report = {}
    cur_report_data = []
    if len(report['data'] == 0):
        return None
    cur_report_type = report['data'][0]['vals']['current']['type']
    cur_report_data.append(''.join([
        'type:', cur_report_type, '\tsort:', report['sort']
    ]))
    for result in report['data']:
        cur_report_data.append(''.join([result['toString']]))

    cur_report['data'] = cur_report_data
    cur_report['sort'] = report['sort']
    cur_report['type'] = cur_report_type

    return cur_report

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

def _get_email_subject():
    return ' '.join(['Testing from magicItch for ', datetime.date.today().isoformat()])

def mail(gmail_user, gmail_pwd, to, subject, text, reports):
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = gmail_user
    msg['Subject'] = subject
    
    msg.attach(MIMEText(text)) 
    
    for report in reports:
        if report is None: continue
        part = MIMEBase('application', 'octet-stream')
        part.set_payload('\n'.join(report['data']))
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                'attachment; filename="%s"' % get_report_filename(report))
        msg.attach(part)
    
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, [gmail_user]+[]+to, msg.as_string())
    mailServer.close()


client = MongoClient('localhost', 27017)
mtg_db = client['mtgo']
c_dl = mtg_db['downloads']
c_prices = mtg_db['prices']
sorts = ['buy', 'sell']
types = ['nonfoil', 'foil', 'pack']

data_seqs = (get_data(cur_type, c_dl, c_prices) for cur_type in types[:1])
reports = (get_report(data_seq, sort_field) for data_seq, sort_field in product(data_seqs, sorts))

files = (prepare_report_files(cur) for cur in reports)
subj = _get_email_subject()
