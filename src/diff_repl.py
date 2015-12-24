from bson.objectid import ObjectId

class DiffStorage:
    def __init__(self, coll, diff_fields, sort_field):
        self.coll = coll
        self.diff_fields = diff_fields
        self.sort = [(sort_field, -1)]

    def get_by_id(self, oid):
        return self.coll.find_one({'_id': ObjectId(oid)})

    def get(self, **kwargs):
        return self.coll.find_one(kwargs)

    def get_by_email(self, email):
        return self.coll.find_one({'email': email})

    def create(self, user):
        return self.coll.insert(user)

    def update(self, updated_user_with_id):
        return self.coll.save(updated_user_with_id)

    def delete(self, user_id):
        return self.coll.remove({'_id': ObjectId(user_id)})

    def add_diff(self, query_dict, obj):
        recent = self.coll.find_one(query_dict, sort=self.sort)
        print 'recent:', recent
        if recent is None:
            print 'inserting and returning:', obj
            self.coll.insert(obj)
            return obj
        # TODO function-ize this for cases and listcomp power
        add_flag = False
        for f in self.diff_fields:
            f_delta = obj[f] - recent[f]
            # TODO get mad over a field collision
            # XXX are there valid diffs that would miss this?
            if f_delta:
                obj[f+'_delta'] = f_delta
                add_flag = True

                if add_flag:
                    # do add and return new obj
                    self.coll.insert(obj)
                    return obj
                else:
                    # skip add but do return an object
                    # TODO determine if this should have the timefield set to new val?
                    # would make it semi-transparent, maybe that is bad
                    return recent

from pymongo import MongoClient
from datetime import datetime
client = MongoClient('kilrog.dyndns.org', 27017)
db = client['diff_testing']
coll = db['diff']
dstore = DiffStorage(coll, ['value'], 'date')
example_obj = {
               'id': 2,
               'date': datetime.utcnow(),
               'value': 1,
               }
example_obj
result = dstore.add_diff({'id':example_obj['id']}, example_obj)
result
"""
{ "_id" : ObjectId("520c2eedd4d97f7c9e973fda"), "sell" : "0.018",
"card_name" : "Guardian of the Ages", "buy" : "0.008",
"date" : ISODate("2013-08-15T01:29:14.998Z"),
"type" : "nonfoil", "set_code" : "M14", "qty" : { "supernova02" : 3, "total" : 4, "ComparePrices" : 1}
dstore = DiffStorage(coll, ['buy', 'sell'], 'date')
#"""



