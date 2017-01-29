"""
This file handles any processing related to map data.
"""
from Static.models import Map, Terrain_Unit_Movement, Version
import logging

maps = {}
movement_dict = {}

def loadMaps(version_name=''):
	"""
	Loads all of the maps into memory for the specified version,
	also calls the function to load the terrain information

	:type version_name: String
	:param version_name: The name of the version for which the maps need to be loaded.\n
					If no version is specified, the lastest version is used

	:rtype: Dictionary
	:return: An object describing the maps loaded, of the form:\n
			 {\n
			 	<Version Name>:{\n
					<Map Name>:{\n
						<X>:{\n
							<Y>:{\n
								"Placement":<Can place here>,\n
								"Terrain":<Terrain Shortname>,\n
							}\n
						}\n
					}\n
			 	}\n
			 }\n
			 Which allows for something like:\n
			 maps["1.0"]["GrassMap"][1][3]["Terrain"] = ?
	"""
	if version_name == '':
		version = Version.objects.latest('pk')
	else:
		version = Version.objects.filter(name=version_name).first()

	map_objects = Map.objects.filter(version=version)
	version_name = version.name
	maps[version_name] = {}
	loadTerrainInfo(version)

	# For each map object in the database for that version
	for mp in map_objects:
		y = -1
		map_name = mp.name
		maps[version_name][map_name] = {}

		# Open each map file for processing
		with open(mp.file_path) as map_file:
			map_as_list = map_file.readlines()

			# Loop over each line
			for line in map_as_list:
				y += 1
				x = -1

				# Split each line into its space-delimited tokens
				for token in line.strip().split(" "):
					x += 1
					if not x in maps[version_name][map_name]:
						maps[version_name][map_name][x] = {}
					maps[version_name][map_name][x][y] = {}

					# Split each token into the comma-delimited objects, with:
					# Object index 0 being the placement information
					# Object index 1 being the terrain type shortname
					split_token = token.split(",")

					# Ensure the correct number of objects is found
					if len(split_token) < 2:
						logging.error("A problem occurred while parsing the map (" + map_name + ") at: X=" + str(x) + " Y=" + str(y) + " for version " + version_name + ".")
						continue

					# The components of the token
					placement = int(split_token[0])
					tile_type = split_token[1]

					# Add the token to the dictionary
					maps[version_name][map_name][x][y] = {"Placement":placement, "Terrain":tile_type}

def loadTerrainInfo(version):
	"""
	Loads terrain movement information for each unit and terrain type.

	:type version: Version object
	:param version: The version of terrain data to load

	:rtype: Dictionary
	:return: An object of the form:\n
			 {\n
				"F":{\n
					"Archer":1,\n
					"Swordsman":2\n
				}\n
			 }\n
			 Notes:\n
			 - The "F" is the shortname for a terrain type\n
			 - The "Archer" is the class name\n
			 - The value is the movement taken to move INTO a token
	"""
	ter_unit_mov = Terrain_Unit_Movement.objects.filter(version=version)

	for tum in ter_unit_mov:
		if not tum.terrain.shortname in movement_dict:
			movement_dict[tum.terrain.shortname] = {}

		movement_dict[tum.terrain.shortname][tum.unit.name] = tum.move

	logging.debug("Movement Dictionary:")
	logging.debug(movement_dict)
	return movement_dict
		