from bson.objectid import ObjectId

class Users:
	def __init__(self, coll):
		self.coll = coll

	#def list(self):
	#	return [usr for usr in self.coll.get()]

	def get(self, user_id):
		return self.coll.find_one({'_id': ObjectId(user_id)})

	def get_by_email(self, email):
		return self.coll.find_one({'email': email})

	def create(self, user):
		return self.coll.insert(user)

	def update(self, updated_user_with_id):
		return self.coll.save(updated_user_with_id)

	def delete(self, user_id):
		return self.coll.remove({'_id': ObjectId(user_id)})