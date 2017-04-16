import os
import sys
import json
import websocket
import socket
import threading
import time
from django.core.management.base import BaseCommand

class PrintColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Command(BaseCommand):
	"""
	Allows for manually creating a websocket and sending data to the server for development testing
	"""

	help = "Creates a websocket to the server for testing purposes."

	def connect(self, url):
		try:
			print(PrintColors.OKBLUE + "Connecting to tactics server at {0}".format(url) + PrintColors.ENDC)
			ws = websocket.create_connection(url, sockopt=((socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),))
			print(PrintColors.OKGREEN + "Connected successfully!" + PrintColors.ENDC)
		except Exception as e:
			print(PrintColors.FAIL + "Failed connecting to tactics server...is it running?" + PrintColors.ENDC)
			print(PrintColors.FAIL + str(e) + PrintColors.ENDC)
			sys.exit(1)

		return ws

	def ping_server(self, ws):
		while True:
			try:
				if 'Stop Ping' not in os.environ:
					ws.send(json.dumps({"PING": "PING"}))
				else:
					break
			except Exception as e:
				pass

			time.sleep(10)
		print("Stopped keepalive thread")

	def process_commands(self, ws, cmd_data):
		print("Processing commands file")
		for cmd in cmd_data:
			print("Sending {0}".format(cmd))
			ws.send(json.dumps(cmd))
			result = ws.recv()
			print("Received {0}".format(result))
		print("Finished processing commands file")

	def add_arguments(self, parser):
		parser.add_argument('--url', type=str, default=None)
		parser.add_argument('--commands', type=str, default=None)

	def handle(self, *args, **options):
		url = options['url']
		if not url:
			url = "ws://localhost:8000"

		ws = self.connect(url)
		t = threading.Thread(target=self.ping_server, args=(ws,))
		t.start()

		commands = options['commands']
		cmd_data = None
		if commands:
			cmd_data = json.load(open(commands, 'r'))
			self.process_commands(ws, cmd_data)

		data = None

		while True:
			data = raw_input("Send (q=quit)>")
			if data == 'q':
				print("Stopping keepalive thread...please wait")
				os.environ['Stop Ping'] = 'True'
				ws.close()
				sys.exit(0)

			try:
				data = json.loads(data)
			except:
				print("Not valid json data")
				continue

			try:
				ws.send(json.dumps(data))
				print(str(ws.recv()))
			except Exception as e:
				print(PrintColors.FAIL + "Failed to send data...reconnecting" + PrintColors.ENDC)
				ws = self.connect(url)
				ws.send(json.dumps(data))
				print(str(ws.recv()))
		
		
