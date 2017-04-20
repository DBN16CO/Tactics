from django.core.management.base import BaseCommand
from Static.create_data import *
from Static.models import Version

class Command(BaseCommand):
	"""
	Provides the ability to initalize the database for a specified version or group of versions\n
	If any version data previously existed for the specified version, it will be skipped,\n
	making the command good for when the database might have important existing data
	"""

	help = "This file will initialize the database using the inputted <version> data"

	def add_arguments(self, parser):
		parser.add_argument('version', nargs="+", type=str)

	def handle(self, *args, **options):
		for version in options['version']:
			ver = Version.objects.filter(name=version).first()

			if ver != None:
				self.stderr.write("Version already exists in database, skipping...")
				continue

			success = setup_static_db(version)
			if success == True:
				self.stdout.write("The database has been successfully created, using version: " + version)
			else:
				self.stderr.write("There was an error while setting up the database, likely invalid version string ("
				 + version + ").")

	