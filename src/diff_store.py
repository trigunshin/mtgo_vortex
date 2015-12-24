from bson.objectid import ObjectId

class DiffStorage:
	def __init__(self, coll, diff_fields, sort_field):
		self.coll = coll
		self.diff_fields = diff_fields
		self.sort_field = sort_field

	#def list(self):
	#	return [usr for usr in self.coll.get()]

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
		recent = self.coll.find(query_dict).sort(self.sort_field, -1)[0]
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
			ret = self.coll.insert(obj)
			return ret
		else:
			# skip add but do return an object
			# TODO determine if this should have the timefield set to new val?
			# would make it semi-transparent, maybe that is bad
			return recent
