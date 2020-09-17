import requests
import json
import time
import random


class VKApi:
	def __init__(self, access_token, group_id, my_token=None):
		self.access_token = access_token
		self.group_id = group_id
		self.my_token = my_token
		self.server = None
		self.ts = None
		self.v = "5.103"
		self.wait="5"
		self.set()
class LongPollApi:
	def __init__(self, access_token, group_id, my_token=None):
		VKApi.__init__(self,              
		self.set()
	def set(self):
		r = requests.get("https://api.vk.com/method/groups.getLongPollServer?group_id="+self.group_id+"&access_token="+self.access_token+"&v=5.103").json()['response']
		self.server=r['server']
		self.key=r['key']
		self.ts=r['ts']
	
	def events(self):
		while 1:
			r = requests.get(self.server+"?act=a_check&key="+self.key+"&ts="+self.ts+"&wait="+self.wait).json()
			updates = r['updates']
			self.ts=r['ts']
			if updates:
				for i in updates:
			


