import datetime
from pymongo import MongoClient
from functools import partial
from itertools import groupby

def toHumanString(card_name, card_set,
                  cur_buy_price, cur_buy_diff,
                  cur_sell_price, cur_sell_diff):#, now_quantity, quantity_diff):
    return ''.join([card_name, " from set ", card_set,
                    " changed buy price by ", ("%05.3f" % (100*cur_buy_diff)),
                    "% to ", str(cur_buy_price),
                    " and sell price by ", ("%05.3f" % (100*cur_sell_diff)),
                    "% to ", str(cur_sell_price)
                    ])

def get_pct_diff(first, second):
    f_first = float(first)
    f_second = float(second)
    if f_second == 0: return 0
    pctdiff = f_first - f_second / f_second
    return pctdiff

def reduce_prices(accum, datum, sub_field_name=None):
    key = datum['set_code'] + datum['card_name']

    if key in accum:
        accum[key][sub_field_name] = datum
    else:
        accum[key] = {sub_field_name: datum,
                      'set': datum['set_code']}
    return accum

client = MongoClient('localhost', 27017)
mtg_db = client['mtgo']

c_dl = mtg_db['downloads']
c_prices = mtg_db['prices']

TYPE = 'nonfoil'
result = c_dl.find({'type':TYPE}).sort([('date', -1)])[0]

current_date = result['date']
td = datetime.timedelta(days=1)
prior_date = current_date - td

# find recent date closest to 24h ago
prior_dl = c_dl.find({'date':{'$gte': prior_date},
                      'type':TYPE}).sort([('date', 1)])[0]
prior_date = prior_dl['date']

# find price data for current and prior dates to compare values
current_data = c_prices.find({'date': current_date,
                              'type': TYPE}).sort([('set_code', 1),
                                                  ('card_name', 1)])
prior_data = c_prices.find({'date': prior_date,
                            'type': TYPE}).sort([('set_code', 1),
                                                 ('card_name', 1)])
cur_dict = reduce(partial(reduce_prices, sub_field_name='current'),
               current_data,
               {})
pdict = reduce(partial(reduce_prices, sub_field_name='prior'),
               prior_data,
               cur_dict)

# XXX sort the values by set before grouping
sorted_vals = sorted(pdict.itervalues(), key=lambda x: x['set'])
grouped = groupby(sorted_vals, lambda x: x['set'])
results = []
for setcode, values in grouped:
    print setcode
    for value in values:
        cur = value['current']
        pri = value['prior']

        buydiff = get_pct_diff(cur.get('buy',0),
                               pri.get('buy',0))
        selldiff = get_pct_diff(cur.get('sell',0),
                               pri.get('sell',0))
        if buydiff > .1 or selldiff > .1:
            printme = toHumanString(cur['card_name'], cur['set_code'],
                          cur.get('buy',0), buydiff, 
                          cur.get('sell', 0), selldiff)
            results.append({
                'vals': value,
                'toString': printme,
                'sort_val': max(buydiff, selldiff)
            })
for result in sorted(results, key=lambda x: x['sort_val'], reverse=True):
    print result['toString']
