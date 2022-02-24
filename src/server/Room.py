from unicodedata import name

class Room():
	def __init__(self,name_, creator_):
		self.name = name_
		self.creator = creator_
		self.users = []
		self.messages = {}

	def get_creator(self):
		return self.creator

	def rename_room(self, new_name):
		self.name = new_name

	def get_users(self):
		return self.users

	def add_user(self, user):
		self.users.append(user)
		
	def remove_user(self, user):
		self.users.remove(user)

	def message(self,time, content):
		self.messages[time] = content
		return self.users
	
	def __str__(self):
		res = '\nName: {}\nCreator: {}\nUsers: {}\nMesages: {}\n'.format(
			self.name, self.creator, self.users, self.message)
		return res