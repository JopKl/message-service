from unicodedata import name


class Message():
	def __init__(self, sender_, content_):
		self.sender = sender_
		self.content = content_
		self.read_by = []

	def add_read(self, user):
		self.read_by.append(user)

class Room():
	def __init__(self,name_, creator_):
		self.name = name_
		self.creator = creator_
		self.users = []
		self.messages = {}

	def rename_room(self, new_name):
		self.name = new_name

	def add_user(self, user):
		self.users.append(user)
		
	def remove_user(self, user):
		self.users.remove(user)

	def message(self,time, sender, content):
		self.messages[time] = Message(sender, content)