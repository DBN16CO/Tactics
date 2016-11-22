from django.core.management.base import BaseCommand
from Static.create_data import *
from Static.models import Version

class Command(BaseCommand):

	help = "This file will initialize the database using the inputted <version> data"

	def add_arguments(self, parser):
		parser.add_argument('version', nargs="+", type=str)

	def handle(self, *args, **options):
		for version in options['version']:
			try:
				ver = Version.objects.get(name=version)
			except Exception:
				pass
			else:
				self.stderr.write("Version already exists in database, exiting...")
				return

			success = setup_static_db(version)
			if success == True:
				self.stdout.write("The database has been successfully created, using version: " + version)
			else:
				self.stderr.write("There was an error while setting up the database, likely invalid version string ("
				 + version + ").")

	