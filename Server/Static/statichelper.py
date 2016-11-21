import logging
from Static.models import Class,Hero_Ability,Leader,Terrain,Version

# Gets the class information for the specified version
# Returns an array of the following form:
# ['Archer','Mage','Flier']
def getClassData(ver_id):
	class_dict = getClassDict(ver_id)

	# Remove all ID keys from the dictionary
	class_array = class_dict.values()

	return class_array

# Gets the leader information for the specified version
# Returns an array of the following form:
# ['Assassin':["Steal","Agility Aura"],
#  'General':["Defense Aura"]
# ]
def getLeaderData(ver_id):
	ability_dict = getHeroAbilDict(ver_id)

	leaders = Leader.objects.filter(version_id=ver_id)

	leader_dict = {}

	for ldr in leaders:
		# Ensure the leader name exists in the dictionary
		if not ldr.name in leader_dict:
			leader_dict[ldr.name] = []

		# Ensure the ability exists in the ability dictionary
		if not ldr.ability_id in ability_dict:
			logging.error("The hero ability dictionary was missing a class (id=" + str(ldr.ability_id) + ").")
			ability_dict[ldr.ability_id] = Leader.objects.get(ldr.ability_id).name

		# Add the specific hero's ability
		leader_dict[ldr.name].append(ability_dict[ldr.ability_id])

	return leader_dict

# Gets the terrain information for the specified version
# Returns a dictionary of thie following form:
# ['grass':
# 	[
# 		'archer':1,	// 1 is move consumed moving over grass for archer
# 		'flier':1,
# 	],
#  'forest':
#  	[
#  		'archer':2,
#  		'flier':1,
#  	]
# ]
def getTerrainData(ver_id):
	# Get all the terrains for that version
	all_ver_terrain = Terrain.objects.filter(version_id=ver_id)
	logging.debug("There are " + str(len(all_ver_terrain)) + " objects in terrain for version " + str(ver_id) + ".")

	class_dict = getClassDict(ver_id)

	terrain_dict = {}

	# Add all the 
	for ter in all_ver_terrain:
		# If the specified terrain has yet to be encountered
		if not ter.name in terrain_dict:
			terrain_dict[ter.name] = {}

		# Ensure that the specified unit(class) ID exists in the dictionary input
		if not ter.unit_id in class_dict:
			logging.error("The passed class dictionary was missing a class (id=" + str(ter.unit_id) + ").")
			class_dict[ter.unit_id] = Class.objects.get(ter.unit_id).name

		# If the specified class doesn't exist in the specific terrain dict
		if not class_dict[ter.unit_id] in terrain_dict[ter.name]:
			terrain_dict[ter.name][class_dict[ter.unit_id]] = ter.move
		else:
			logging.error("Duplicate unit class for terrain type.")

	return terrain_dict

"""
All internal helper classes for this 'Class' below this line
"""
# Gets the class information for the specified version including the ID
def getClassDict(ver_id):
	# Get all the classes for that version
	all_ver_classes = Class.objects.filter(version_id=ver_id)

	class_dict = {}

	# Add each class name to the dictionary
	for clss in all_ver_classes:
		class_dict[clss.id] = clss.name

	return class_dict

# Gets the hero ability information for the specified version including the ID
def getHeroAbilDict(ver_id):
	# Get all the classes for that version
	all_ver_hero_abil = Hero_Ability.objects.filter(version_id=ver_id)

	hero_abil_dict = {}

	# Add each hero ability name to the dictionary
	for hb in all_ver_hero_abil:
		hero_abil_dict[hb.id] = hb.name

	return hero_abil_dict