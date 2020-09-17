import requests
import json
import time
import random
from collections import deque


class VKApi:
	def __init__(self, access_token, group_id, my_token=None):
		self.access_token = access_token
		self.group_id = group_id
		self.my_token = my_token
		self.server = None
		self.ts = None
		self.v = "5.103"
		self.wait="5"
	def message_send(self,peer_id,message,keyboard=None):
		random_id=str(random.randint(-2147483648,2147483647))
		data={"peer_id":peer_id, "random_id":random_id,"access_token":self.access_token,  "v":self.v, "message":message, "keyboard": keyboard}
		print(data)
		response=requests.post("https://api.vk.com/method/messages.send",data).json()
		print(response)
	def send_audio(self,peer_id,filename="cache/filtered_audio.mp3"):
		p = requests.get("https://api.vk.com/method/docs.getUploadServer?access_token="+self.my_token+"&group_id="+self.group_id+"&type=audio_message&v=5.103").json()
		print(p)
		time.sleep(1)
		upload_url=p['response']['upload_url']
		upload_files = {'file': (filename, open(filename, 'rb'))}
		response = requests.post(upload_url, files=upload_files)
		time.sleep(1)
		file=response.json()["file"]
		p = requests.get("https://api.vk.com/method/docs.save?file="+file+"&access_token="+self.my_token+"&v=5.103").json()
		print(p)
		time.sleep(1)
		try:
		    p=p['response']['audio_message']
		except KeyError:
		    captcha_sid=p['error']['captcha_sid']
		    captcha_img=p['error']['captcha_img']
		    print(captcha_img)
		    captcha_key=str(input())
		    p = requests.get("https://api.vk.com/method/docs.save?file="+file+"&access_token="+self.my_token+"&captcha_sid="+str(captcha_sid)+"&captcha_key="+captcha_key+"&v=5.103").json()
		    p=p['response']['audio_message'] 
		media_id=str(p["id"])
		random_id=str(random.randint(-9223372036854775808,9223372036854775807))
		response=requests.post("https://api.vk.com/method/messages.send?peer_id="+peer_id+"&random_id="+random_id+"&attachment=doc-"+self.group_id+"_"+media_id+"&access_token="+self.access_token+"&v=5.103")

class Command():
	def __init__(self,peer_id,from_id,command):
		self.type = "command"
		self.peer_id = str(peer_id)
		self.from_id = str(from_id)
		self.command = command
		
class User():
	def __init__(self,peer_id,from_id):
		self.type = "user"
		self.peer_id = str(peer_id)
		self.from_id = str(from_id)
		self.request={}
		self.mods={}
		
class LongPollApiBot(VKApi):
	def __init__(self, access_token, group_id, my_token=None):
		VKApi.__init__(self, access_token, group_id, my_token)
		self.set()
	def set(self):
		r = requests.get("https://api.vk.com/method/groups.getLongPollServer?group_id="+self.group_id+"&access_token="+self.access_token+"&v=5.103").json()['response']
		self.server=r['server']
		self.key=r['key']
		self.ts=r['ts']
	def get_messages(self, msg, all_messages=None):
		if all_messages == None:
				all_messages = []
		e=msg.pop('fwd_messages', None)		
		all_messages.append(msg)
		if e:
			for i in e:
				self.get_messages(i,all_messages)
		return all_messages
				
	def events(self):
		while 1:
			r = requests.get(self.server+"?act=a_check&key="+self.key+"&ts="+self.ts+"&wait="+self.wait).json()
			updates = r['updates']
			self.ts=r['ts']
			if updates:
				for i in updates:
					message = i['object']['message']
					print("-----------------")
					print("UPDATE:")
					print(i)
					print("-----------------")
					from_id = message['from_id']
					peer_id = message['peer_id']
					payload = message.get('payload',None)
					if payload != None:
						payload = json.loads(payload)
						r = Command(peer_id, from_id, payload['command'])
					else:
						r = User(peer_id, from_id)
						r.request=self.get_messages(message)
						r.request=list(filter(lambda x: x['attachments'], r.request))
						r.request=list(filter(lambda x: x['attachments'], r.request))
					yield r
					'''
					r={}
					r['from_id']=from_id
					r['peer_id']=peer_id
					if payload != None:
						payload = json.loads(payload)
						r["command"]=payload.get('command')
					else:
						p={}
						p['request']=self.get_messages(message)
						p['request']=list(filter(lambda x: x['attachments'], p['request']))
						p['request']=list(filter(lambda x: x['attachments'][0]['type'] == 'audio_message', p['request']))
						p['mods']={}
						r[peer_id]=p
					yield r'''		
