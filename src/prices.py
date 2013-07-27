from codecs import open
import httplib
from urllib2 import urlopen
from datetime import datetime
import json
import re
from itertools import groupby
from functools import partial
from pymongo import MongoClient

######## some internet hack i need to put into a lib and import
# from http://effbot.org/zone/unicode-convert.htm
import unicodedata, sys

CHAR_REPLACEMENT = {
    # latin-1 characters that don't have a unicode decomposition
    0xc6: u"AE", # LATIN CAPITAL LETTER AE
    0xd0: u"D",  # LATIN CAPITAL LETTER ETH
    0xd8: u"OE", # LATIN CAPITAL LETTER O WITH STROKE
    0xde: u"Th", # LATIN CAPITAL LETTER THORN
    0xdf: u"ss", # LATIN SMALL LETTER SHARP S
    0xe6: u"ae", # LATIN SMALL LETTER AE
    0xf0: u"d",  # LATIN SMALL LETTER ETH
    0xf8: u"oe", # LATIN SMALL LETTER O WITH STROKE
    0xfe: u"th", # LATIN SMALL LETTER THORN
    }

##
# Translation dictionary.  Translation entries are added to this
# dictionary as needed.
class unaccented_map(dict):
    ##
    # Maps a unicode character code (the key) to a replacement code
    # (either a character code or a unicode string).

    def mapchar(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        de = unicodedata.decomposition(unichr(key))
        if de:
            try:
                ch = int(de.split(None, 1)[0], 16)
            except (IndexError, ValueError):
                ch = key
        else:
            ch = CHAR_REPLACEMENT.get(key, key)
        self[key] = ch
        return ch

    if sys.version >= "2.5":
        # use __missing__ where available
        __missing__ = mapchar
    else:
        # otherwise, use standard __getitem__ hook (this is slower,
        # since it's called for each character)
        __getitem__ = mapchar
unicode_translation_map = unaccented_map()
######## end horrible unicode hack from the internet

name_set_pattern = "(?P<card_name>.*)\s\[(?P<set_code>\w*)\]"
name_set_regex = regex = re.compile(name_set_pattern)

# set/card info data
def load_set_data(set_data_file_name='AllSets.json'):
    with open(set_data_file_name, encoding='utf-8') as f:
        setinfo = json.load(f)
    set_data = {}
    for k,v in setinfo.iteritems():
        cur_card_dict = {}
        for card in v['cards']:
            cur_card_dict[card['name']] = card
        set_data[k] = cur_card_dict
    return set_data
def upload_set_data(db, data, coll_name='set_data'):
    return db[coll_name].insert(data)

# functions for supernova parsing
def update_with_type(data_dict):
    name = data_dict['card_name']
    if name.startswith("Foil "):
        data_dict['card_name'] = name[5:]
        data_dict['type'] = 'foil'
    elif name.endswith(" BOOSTER"):
        data_dict['type'] = "booster"
    else:
        data_dict['type'] = 'nonfoil'
    return data_dict
def parse_name_set(raw_name):
    ret = name_set_regex.search(raw_name).groupdict()
    ret['card_name'] = ret['card_name'].decode('unicode-escape').translate(unicode_translation_map).encode("ascii", "ignore")
    ret.update(update_with_type(ret))
    return ret
def line_to_arr(line):
    return filter(None, re.split(r'\s{2,}', line))
def case_both(arr):
    ret = {'buy': arr[1].strip(),
           'sell': arr[2].strip(),
           'bots': arr[3].strip()}
    ret.update(parse_name_set(arr[0]))
    return ret
def case_no_stock(arr):
    ret = {'buy': arr[1].strip()}
    ret.update(parse_name_set(arr[0]))
    return ret
def case_not_buying(arr):
    ret = {'sell': arr[1].strip(),
           'bots': arr[2].strip()}
    ret.update(parse_name_set(arr[0]))
    return ret
# dispatch functions by array length
arr_cases = {
    4:case_both,
    2:case_no_stock,
    3:case_not_buying,
}
def parse_quantity(data_obj):
    qty = {'total': 0}
    try:
        botstring = data_obj['bots']
        for bot in botstring.split(' '):
            spl = bot.split('[')
            bot_name = spl[0]
            bot_quantity = spl[1].split(']')[0]
            qty[bot_name] = int(bot_quantity)
            qty['total'] += int(bot_quantity)
            del data_obj['bots']
    except KeyError,e:
        # if bots field doesn't exist there's no stock
        pass
    data_obj['qty'] = qty
    return data_obj
def data_dict_from_arr(arr, date=None):
    arr_len = len(arr)
    try:
        ret = arr_cases[arr_len](arr)
        ret = parse_quantity(ret)
        if date is not None:
            ret['date'] = date
    except KeyError,e:
        ret = None
    except AttributeError,e:
        ret = None
    return ret
def pprint_card(card):
    print "%(card_name)s %(sell)s %(set_code)s" % card
def get_remote_file_lines(url):
    response = urlopen(url)
    content = response.read().split('\n')
    return content
def get_card_data(line_array, data_date):
    data_dicts = (data_dict_from_arr(line_to_arr(cur_line),
                                     data_date)
                  for cur_line in line_array if cur_line)
    # filter out empty cases and return generator
    return filter(None, data_dicts)
def upload_data(db, data, data_date,
                vendor='supernova',
                price_name='prices',
                dl_name='downloads'):
    # upload results first

    db[price_name].insert(data)
    # any errors will skip this step; query for this first to ensure valid runs
    db[dl_name].insert({
                        'vendor':vendor,
                        'date': data_date,
                        'type': price_name
                        })
    return
def get_local_data_file_lines(file_name="prices_0.txt"):
    with open(file_name, encoding='utf-8') as f:
        content = f.readlines()
    return content

# higher level functions
def do_remote_update():
    client = MongoClient('localhost', 27017)
    mtg_db = client['mtgo']
    files = [
             'http://www.supernovabots.com/prices_0.txt',
             'http://www.supernovabots.com/prices_3.txt',
             'http://www.supernovabots.com/prices_6.txt']
    parse_date = datetime.utcnow()
    for path in files:
        lines = get_remote_file_lines(path)
        data = get_card_data(lines[7:], parse_date)
        dd = list(data)
        upload_data(mtg_db, data, parse_date)
    return True

# TODO implement AllSets storage/retrieval in/from the db
# TODO figure out if the above should be a single doc or set by set

def get_set_groups(card_data):
    groups = groupby(card_data, lambda x: x['set_code'])
    group_colls = []
    uniquekeys = []
    for k, g in groups:
        group_colls.append(list(g)) # Store group iterator as a list
        uniquekeys.append(k)
    #return {'groups':group_colls, 'keys':uniquekeys}
    return (uniquekeys, group_colls)
def isMythic(set_info, supernova_card):
    try:
        card_set = supernova_card['set_code']
        # take first name of a split card, or whole name of a normal card
        card_name = supernova_card['card_name'].split('/')[0]

        rr=set_info[card_set][card_name]['rarity']
        ret = (set_info[card_set][card_name]['rarity'] == 'Mythic Rare')
        #print card_name, rr, ret
    except KeyError,e:
        # unknown sets
        ret = False
    return ret
def price_recent_mythics():
    lines = get_local_data_file_lines()
    data = get_card_data(lines[7:], datetime.utcnow())

    keys,groups = get_set_groups(data)

    set_data = load_set_data('AllSets.json')
    #set_data['DGM']['Deadbridge Chant']['rarity'] == 'Mythic Rare'
    m_part = partial(isMythic, set_data)
    mythics = filter(m_part, data)
    #for key in keys[0:5]:
    for m in mythics[0:20]:
        pprint_card(m)

    """
    for card in data:
        try:
            if set_data[card['set_code']][card['card_name'].split('/')[0]]['rarity'] == 'Mythic Rare':
                if float(card['buy']) < .6:
                    pprint_card(card)
        except KeyError,e:
            print '\terror: ', card['card_name']
    """
    return

#price_recent_mythics()
do_remote_update()
"""
lines = get_local_data_file_lines()
data = get_card_data(lines[7:], datetime.utcnow())

keys,groups = get_set_groups(data)

set_data = load_set_data('AllSets.json')
dgm=set_data['DGM']
mm=partial(isMythic, set_data)
mm(data[37])
filter(mm, data[0:37])
isMythic(set_data, list(data[37]))
def get_name(card):
    return card['name']
map(get_name, dgm.itervalues())
#"""