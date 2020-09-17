from VKApi_wrapper import LongPollApiBot
from VKApi_wrapper import VKApi
from rnnoise_wrapper import RNNoise
from pydub import AudioSegment
import threading
import collections
import json
import time
import requests

access_token = ""
group_id=""
my_token=""
queue = []

class Processing (threading.Thread):
	def __init__(self, name, counter):
		threading.Thread.__init__(self)
		self.threadID = counter
		self.name = name
		self.counter = counter
	def noise(self,link):
		denoiser=RNNoise()
		r=requests.get(link)
		with open("cache/audio.mp3","wb") as audio:
			audio.write(r.content)
		audio = AudioSegment.from_mp3("cache/audio.mp3")
		filtered_audio = denoiser.filter(audio)
		filtered_audio.export("cache/filtered_audio.mp3",format="mp3")

	def run(self):
		print("Starting " + self.name)
		api = VKApi(access_token, group_id,my_token)
		while 1:
			for user in queue:
				request=user.request.pop(0)
				link=request['attachments'][0]['audio_message']['link_mp3']
				waveform=request['attachments'][0]['audio_message']['waveform']
				mods=user.mods
				print(mods)
				for mod in mods:
					if mod == "noise":
						self.noise(link)
				api.send_audio(user.peer_id)
				if not user.request:
					queue.remove(user)
				print(queue)
		print("Exiting " + self.name)

class Updating (threading.Thread):
	def __init__(self, name, counter):
		threading.Thread.__init__(self)
		self.threadID = counter
		self.name = name
		self.counter = counter
	def run(self):
		print("Starting " + self.name)
		bot = LongPollApiBot(access_token, group_id)
		api = VKApi(access_token, group_id)
		events = bot.events()
		users = {}
		default_keyboard = {"one_time":False,"buttons":[[{"action":{"type":"text","label":u"Убрать шум", "payload":{"command":"noise"}},"color":"secondary"},{"action":{"type":"text","label":u"Ускорить/Замедлить","payload":{"command":"speed"}},"color":"secondary"},{"action":{"type":"text","label":u"Поменять громкость","payload":{"command":"volume"}},"color":"secondary"}],[{"action":{"type":"text","label":u"Отменить","payload":{"command":"cancel"}},"color":"secondary"},{"action":{"type":"text","label":u"Готово","payload":{"command":"done"}},"color":"secondary"}]]}
		for i in events:
			if i.type == "command":
				if i.command == "noise":
					users[i.peer_id].mods["noise"] = True
				elif i.command == "speed":
					k = {"one_time":True,"buttons":[[{"action":{"type":"text","label":"0,5x", "payload":{"command":"0,5x"}},"color":"secondary"},{"action":{"type":"text","label":u"1,5x","payload":{"command":"1,5x"}},"color":"secondary"},{"action":{"type":"text","label":u"2x","payload":{"command":"2x"}},"color":"secondary"},{"action":{"type":"text","label":u"Назад","payload":{"command":"back"}},"color":"secondary"}]]}
					keyboard = json.dumps(k, ensure_ascii = False)
					print(type(keyboard))
					api.message_send(i.peer_id,"f",keyboard)
					users[i.peer_id].mods["speed"] = True
				elif i.command == "volume":
					k = {"one_time":True,"buttons":[[{"action":{"type":"text","label":u"-1дБ", "payload":{"command":"-1дБ"}},"color":"secondary"},{"action":{"type":"text","label":u"+1дБ","payload":{"command":"+1дБ"}},"color":"secondary"}],[{"action":{"type":"text","label":u"Назад","payload":{"command":"back"}},"color":"secondary"}]]}
					keyboard = json.dumps(k, ensure_ascii = False)
					api.message_send(i.peer_id,"f", keyboard)
				elif i.command == "0,5x":
					users[i.peer_id].mods["speed"] = 0,5
					kb=json.dumps(default_keyboard, ensure_ascii=False)
					print(kb)
					api.message_send(i.peer_id,"Выберите, что хотите изменить",keyboard=kb)
				elif i.command == "1,5x":
					users[i.peer_id].mods["speed"] = 1,5
					kb=json.dumps(default_keyboard, ensure_ascii=False)
					print(kb)
					api.message_send(i.peer_id,"Выберите, что хотите изменить",keyboard=kb)
				elif i.command == "2x":
					users[i.peer_id].mods["speed"] = 2
					kb=json.dumps(default_keyboard, ensure_ascii=False)
					print(kb)
					api.message_send(i.peer_id,"Выберите, что хотите изменить",keyboard=kb)
				elif i.command == "-1дБ":
					users[i.peer_id].mods["volume"] = 1
					kb=json.dumps(default_keyboard, ensure_ascii=False)
					print(kb)
					api.message_send(i.peer_id,"Выберите, что хотите изменить",keyboard=kb)
				elif i.command == "+1дБ":
					users[i.peer_id].mods["volume"] = -1
					kb=json.dumps(default_keyboard, ensure_ascii=False)
					print(kb)
					api.message_send(i.peer_id,"Выберите, что хотите изменить",keyboard=kb)
				elif i.command == "back":
					keyboard=json.dumps(default_keyboard, ensure_ascii=False)
					api.message_send(i.from_id,"Выберите, что хотите изменить",keyboard)
				elif i.command == "cancel":
					users.pop(i.peer_id,None)
					kb = {"one_time":False,"buttons":[]}
					kb=json.dumps(kb, ensure_ascii=False)
					print(kb)
					api.message_send(i.peer_id,"Отменено",kb)
				elif i.command == "done":
					queue.append(users[i.peer_id])
					users.pop(i.peer_id,None)
					kb = {"one_time":False,"buttons":[]}
					kb=json.dumps(kb, ensure_ascii=False)
					api.message_send(i.peer_id,"Добавлено в очередь",kb)
					print(queue)
			elif i.type == "user":
				print("user")
				users[i.peer_id]=i
				if not i.request:
				 	api.message_send(i.peer_id,"Голосовое сообщение не получено!")
				else:
					api.message_send(i.peer_id,"Голосовое сообщение получено")
					kb=json.dumps(default_keyboard, ensure_ascii=False)
					print(kb)
					api.message_send(i.peer_id,"Выберите, что хотите изменить",keyboard=kb)
		print("Exiting " + self.name)

thread1 = Updating("Updating", 1)
thread1.start()
thread2 = Processing("Processing", 2)
thread2.start()
thread2.join()
thread1.join()
print("end")
