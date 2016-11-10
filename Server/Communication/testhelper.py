from channels import Channel
from channels.tests import ChannelTestCase
from router import *
from Server.config import *
from Static.models import Version, Action, Class, Hero_Ability, Leader, Map, Perk, Stat
from Game.models import Unit

class TestHelper(ChannelTestCase):
	def __init__(self):
		self.channel = Channel(u'Test')
		self.setupConfig()
		self.initStaticData()

	def setupConfig(self):
		startup()

	def send(self, payload):
		self.channel.send({u'bytes': payload, u'reply_channel': u'Test'})
		message = self.get_next_message(u'Test', require=True)
		processRequest(message)

	def receive(self):
		result = self.get_next_message(u'Test', require=True)
		return result.content['text']

	def initStaticData(self):
		# Ensure that the data does not already exist
		if Version.objects.count() > 0:
			return

		# Create the version value in the database
		version = "1.0"
		verObject = Version(name=version)
		verObject.save()
		ver_id = verObject.id
		logging.debug("Version ID is " + str(ver_id))
		
		# Data for the tables
		actions=["Attack","Wait","Move","Heal"]
		classes=["Archer", "Mage", "Healer", "Swordsman", "Horseman", "Flier", "Thief"]
		hero_abils=["Extra Range", "Steal", "Regen Aura", ]
		leaders=["Sniper","General","Assassin"]
		perks=["Extra Money", "Strong Arrows", "Forest Fighter"]
		#map
		stats=["HP","Move","Agility","Intelligence","Strength","Luck"]

		# Create the actions
		for actn in actions:
			actionObject = Action(name=actn, version_id=ver_id)
			actionObject.save()

		# Create the classes
		for clas in classes:
			classObject = Class(name=clas, version_id=ver_id)
			classObject.save()

		# Create the hero abilities
		for heroAbil in hero_abils:
			heroAbilObject = Hero_Ability(name=heroAbil, version_id=ver_id)
			heroAbilObject.save()

		# Create the leaders
		for ldr in classes:
			for abil_id in Hero_Ability.objects.values_list('pk', flat=True):
				leaderObject = Leader(name=ldr, ability_id=abil_id, version_id=ver_id)
				leaderObject.save()

		# Create the perks
		for prk in perks:
			perkObject = Perk(name=prk, version_id=ver_id)
			perkObject.save()

		# Create the stats
		counter=0
		for stt in stats:
			for unt in Class.objects.values_list('pk', flat=True):
				counter += 1
				statObject = Stat(name=stt, unit_id=unt, value=counter, version_id=ver_id)
				statObject.save()