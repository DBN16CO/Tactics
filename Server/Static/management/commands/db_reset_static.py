from django.core.management.base import BaseCommand
from Static.create_data import *
from Static.models import Version, Terrain_Unit_Movement, Unit_Stat, Terrain, Stat, Map, Perk, Leader_Ability, Leader, Class, Action, Ability

class Command(BaseCommand):
	"""
	Provides the ability to initalize the database for a specified version or group of versions\n
	If any version data previously existed for the specified version, it will be erased,\n
	making the command good for development, but very dangerous to use in a production-level environment
	"""

	help = "This file will initialize the database using the inputted <version> data"

	def add_arguments(self, parser):
		parser.add_argument('version', nargs="+", type=str)

	def handle(self, *args, **options):
		for version in options['version']:
			ver = Version.objects.filter(name=version).first()

			if ver == None:
				self.stderr.write("Version (" + ver.name + ") does not exist, not dropping any values...")
				continue

			self.clearDB(ver)

			success = setup_static_db(version)
			if success == True:
				self.stdout.write("The database has been successfully created, using version: " + version)
			else:
				self.stderr.write("There was an error while setting up the database, likely invalid version string ("
				 + version + ").")

	def clearDB(self, ver):
		# Remove all values that match the given ID
		# Terrain_Unit_Movement
		count = Terrain_Unit_Movement.objects.filter(version_id=ver.id).count()
		self.stdout.write("Removing (" + str(count) + ") objects from Terrain_Unit_Movement.")
		Terrain_Unit_Movement.objects.filter(version_id=ver.id).delete()
		# Unit_Stat
		count = Unit_Stat.objects.filter(version_id=ver.id).count()
		self.stdout.write("Removing (" + str(count) + ") objects from Unit_Stat.")
		Unit_Stat.objects.filter(version_id=ver.id).delete()
		# Terrain
		count = Terrain.objects.filter(version_id=ver.id).count()
		self.stdout.write("Removing (" + str(count) + ") objects from Terrain.")
		Terrain.objects.filter(version_id=ver.id).delete()
		# Stat
		count = Stat.objects.filter(version_id=ver.id).count()
		self.stdout.write("Removing (" + str(count) + ") objects from Stat.")
		Stat.objects.filter(version_id=ver.id).delete()
		# Map
		count = Map.objects.filter(version_id=ver.id).count()
		self.stdout.write("Removing (" + str(count) + ") objects from Map.")
		Map.objects.filter(version_id=ver.id).delete()
		# Perk
		count = Perk.objects.filter(version_id=ver.id).count()
		self.stdout.write("Removing (" + str(count) + ") objects from Perk.")
		Perk.objects.filter(version_id=ver.id).delete()
		# Leader_Ability
		count = Leader_Ability.objects.filter(version_id=ver.id).count()
		self.stdout.write("Removing (" + str(count) + ") objects from Leader_Ability.")
		Leader_Ability.objects.filter(version_id=ver.id).delete()
		# Leader
		count = Leader.objects.filter(version_id=ver.id).count()
		self.stdout.write("Removing (" + str(count) + ") objects from Leader.")
		Leader.objects.filter(version_id=ver.id).delete()
		# Class
		count = Class.objects.filter(version_id=ver.id).count()
		self.stdout.write("Removing (" + str(count) + ") objects from Class.")
		Class.objects.filter(version_id=ver.id).delete()
		# Action
		count = Action.objects.filter(version_id=ver.id).count()
		self.stdout.write("Removing (" + str(count) + ") objects from Action.")
		Action.objects.filter(version_id=ver.id).delete()
		# Ability
		count = Ability.objects.filter(version_id=ver.id).count()
		self.stdout.write("Removing (" + str(count) + ") objects from Ability.")
		Ability.objects.filter(version_id=ver.id).delete()
		# Version
		count = Version.objects.filter(id=ver.id).count()
		self.stdout.write("Removing (" + str(count) + ") objects from Version.")
		Version.objects.filter(id=ver.id).delete()