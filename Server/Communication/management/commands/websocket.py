import threading
import json
from django.core.management.base import BaseCommand
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory

class Server(WebSocketClientProtocol):

	def onConnect(self, request):
		print("Client connecting: {}".format(request.peer))

	def onOpen(self):
		print("WebSocket connection open.")

	def onMessage(self, payload, isBinary):
		if isBinary:
			print("Binary message received: {} bytes".format(len(payload)))
		else:
			print("Text message received: {}".format(payload.decode('utf8')))

	def onClose(self, wasClean, code, reason):
		print("WebSocket connection closed: {}".format(reason))

	@classmethod
	def broadcast_message(cls, data):
		payload = json.dumps(data, ensure_ascii = False).encode('utf8')
		reactor.callFromThread(cls.sendMessage, payload)

class Command(BaseCommand):
	"""
	Allows for manually creating a websocket and sending data to the server for development testing
	"""

	help = "Creates a websocket to the server for testing purposes."

	@classmethod
	def prompt(cls):
		data = None

		while True:
			data = raw_input("Send (q=quit)>")
			if data == 'q':
				break

			Server.broadcast_message(data)

	def add_arguments(self, parser):
		#parser.add_argument('version', nargs="+", type=str)
		pass

	def handle(self, *args, **options):
		t= threading.Thread(target=Command.prompt)
		t.start()
		factory = WebSocketClientFactory(u"ws://127.0.0.1:8000")
		factory.protocol = Server

		reactor.connectTCP("127.0.0.1", 8000, factory)
		reactor.run()
		
