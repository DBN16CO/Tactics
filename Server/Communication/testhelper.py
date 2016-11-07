from channels import Channel
from channels.tests import ChannelTestCase
from router import *
from Server.config import *

class TestHelper(ChannelTestCase):
	def __init__(self):
		self.channel = Channel(u'Test')
		self.setupConfig()

	def setupConfig(self):
		startup()

	def send(self, payload):
		self.channel.send({u'bytes': payload, u'reply_channel': u'Test'})
		message = self.get_next_message(u'Test', require=True)
		processRequest(message)

	def receive(self):
		result = self.get_next_message(u'Test', require=True)
		return result.content['text']