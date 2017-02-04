"""
.. module:: create_data
   :synopsis: Creates all of the Static data in the database for each version

.. moduleauthor:: Drew, Brennan, and Nick

"""
from Static.models import Version, Ability, Action, Class, Class_Action, Leader, Leader_Ability, Perk, Map, Stat, Unit_Stat, Terrain, Terrain_Unit_Movement
import logging

def setup_static_db(version):
	"""
	Sets up the static database tables with all the information necessary for the specified version

	:type version: String
	:param version: The name of the version to populate

	:rtype: Boolean
	:return: True only if the provided version's definition exists later in the module, currently includes versions:\n
			 1.0
	"""
	cmd = {
		"1.0":ver_1_0_static_data
	}

	if not version in cmd:
		logging.error("Specified version does not exist.")
		return False

	# Load the data for the specified version
	data = cmd[version]()

	# Save the version data
	logging.info("Creating Version object...")
	ver = Version(name=data["Version"]["Name"], price_max=data["Version"]["Price_Max"],
		unit_count=data["Version"]["Unit_Count"])
	ver.save()

	# Save the Ability Data
	logging.info("Creating Ability objects...")
	for abil in data["Abilities"].keys():
		abil_inst = Ability(name=abil, description=data["Abilities"][abil], version=ver)
		abil_inst.save()

	# Save the action data
	logging.info("Creating Action objects...")
	for actn in data["Actions"].keys():
		action = Action(name=actn, description=data["Actions"][actn], version=ver)
		action.save()

	# Save the Leader Data
	logging.info("Creating Leader objects...")
	for ldr in data["Leaders"]:
		ldr_inst =  Leader(name=ldr, description=data["Leaders"][ldr]["Description"], version=ver)
		ldr_inst.save()
		for abil in data["Leaders"][ldr]["Abilities"]:
			ability = Ability.objects.get(name=abil, version=ver)
			ldr_abil_inst = Leader_Ability(leader=ldr_inst, ability=ability, version=ver)
			ldr_abil_inst.save()

	# Save the Perk Data
	logging.info("Creating Perk objects...")
	for prk in data["Perks"].keys():
		perk_inst = Perk(name=prk, description=data["Perks"][prk]["Description"],
			tier=data["Perks"][prk]["Tier"], version=ver)
		perk_inst.save()

	# Save the Map Data
	logging.info("Creating Map objects...")
	for mp in data["Maps"].keys():
		map_inst = Map(name=mp, file_path=str(data["Map_Base"]) + data["Maps"][mp], version=ver)
		map_inst.save()

	# Save the Stat Data
	logging.info("Creating Stat objects...")
	for stt in data["Stats"].keys():
		stt_inst = Stat(name=stt, description=data["Stats"][stt]["Description"], version=ver)
		stt_inst.save()

	# Save the Terrain Data
	logging.info("Creating Terrain objects...")
	for ter in data["Terrain"].keys():
		ter_inst = Terrain(name=data["Terrain"][ter]["DisplayName"],
			description=data["Terrain"][ter]["Description"], shortname=ter, version=ver)
		ter_inst.save()

	# Save the class data
	logging.info("Creating Class objects...")
	for clss in data["Classes"].keys():
		clss_inst = Class(name=clss, attack_type=data["Classes"][clss]["AttackType"],
			description=data["Classes"][clss]["Description"],
			price=data["Classes"][clss]["Price"], version=ver)
		clss_inst.save()

		# Set the class' actions
		for actn in data["Classes"][clss]["Actions"].keys():
			if data["Classes"][clss]["Actions"][actn]:
				action = Action.objects.get(name=actn, version=ver)
				clss_actn_inst = Class_Action(clss=clss_inst, action=action, version=ver)
				clss_actn_inst.save()

		# Set the class' stats
		for stt in data["Classes"][clss]["Stats"].keys():
			stat = Stat.objects.get(name=stt, version=ver)
			stt_unit_inst = Unit_Stat(stat=stat, unit=clss_inst,
				value=data["Classes"][clss]["Stats"][stt], version=ver)
			stt_unit_inst.save()

		# Set the class' movement
		for ter in data["Classes"][clss]["Terrain"].keys():
			terrain = Terrain.objects.get(shortname=ter, version_id=ver.id)
			ter_unt_mv_inst = Terrain_Unit_Movement(terrain=terrain, unit=clss_inst,
				move=data["Classes"][clss]["Terrain"][ter], version=ver)
			ter_unt_mv_inst.save()

	return True

# Supplies all necessary setup data for version 1.0 of the game
def ver_1_0_static_data():
	"""
	The definition of version 1.0 of Tactics.\n
	Provides a return object detailing any information for the version.

	:rtype: Dictionary
	:return: All values necessary to properly populate the Static database tables for version 1.0
	"""
	data = {}

	# Version Data
	data["Version"] = {
		"Name":"1.0",
		"Price_Max":2000,
		"Unit_Count":3,
	}

	# Hero Ability Data
	data["Abilities"] = {
		"Extra Range":  "Increase the maximum range of nearby range attacks by 1.",
		"Steal":        "Provides nearby units the ability to steal items from the enemy.",
		"Defense Aura": "Increases the defense of nearby units.",
		"Evasion Aura": "Increases the chance your units will dodge an attack.",
	}

	# Action Data
	data["Actions"] = {
		"Attack": "Deal damage to target unit.",
		"Heal":   "Restore health to target allied unit.",
		"Wait":   "End move without taking action."
	}

	# Class Data
	data["Classes"] = {
		"Archer":    {
			"AttackType":"Physical",
			"Description":"Ranged unit with low armor.  Good at defeating Fliers.",
			"Actions":{"Attack":True,"Heal":False,"Wait":True},
			"Stats": {
				"HP":10.0, "Move": 6.0, "Agility": 8.5, "Intelligence": 4.0, "Strength": 7.0, "Luck": 7.0, "Defense":3, "Resistance":6, "Attack Range":2,
			},
			"Terrain": {
				"G": 1.0, "F": 2.0, "W":99.0, "M": 4.0, "R": 1.0,
			},
			"Price":150,
		},
		"Swordsman": {
			"AttackType":"Physical",
			"Description":"Standard melee unit with average stats.",
			"Actions":{"Attack":True,"Heal":False,"Wait":True},
			"Stats": {
				"HP":15.0, "Move": 5.0, "Agility": 6.0, "Intelligence": 3.0, "Strength": 6.0, "Luck": 5.0, "Defense":5, "Resistance":4, "Attack Range":1,
			},
			"Terrain": {
				"G": 1.0, "F": 3.0, "W":99.0, "M": 4.0, "R": 1.0,
			},
			"Price":100,
		},
		"Mage":      {
			"AttackType":"Magical",
			"Description":"Magical ranged attacker with low defense.  Good at defeating armored units.",
			"Actions":{"Attack":True,"Heal":False,"Wait":True},
			"Stats": {
				"HP":10.0, "Move": 5.0, "Agility": 5.0, "Intelligence":10.5, "Strength": 1.0, "Luck": 7.0, "Defense":2, "Resistance":8, "Attack Range":2,
			},
			"Terrain": {
				"G": 1.0, "F": 2.0, "W":99.0, "M": 3.0, "R": 1.0,
			},
			"Price":150,
		},
		"Cleric":      {
			"AttackType":"Magical",
			"Description":"Magical ranged healing unit with low defense.  Restores weak units so they can return to battle.",
			"Actions":{"Attack":False,"Heal":True,"Wait":True},
			"Stats": {
				"HP":5.0, "Move": 5.0, "Agility": 5.0, "Intelligence":10, "Strength": 1.0, "Luck": 5.0, "Defense":2, "Resistance":9, "Attack Range":2,
			},
			"Terrain": {
				"G": 1.0, "F": 2.0, "W":99.0, "M": 3.0, "R": 1.0,
			},
			"Price":200,
		},
		"Rogue":     {
			"AttackType":"Physical",
			"Description":"Fast evasive melee unit.  Has low defense but high attack potential.",
			"Actions":{"Attack":True,"Heal":False,"Wait":True},
			"Stats": {
				"HP":10.0, "Move": 6.0, "Agility":10.5, "Intelligence": 4.0, "Strength": 3.0, "Luck":11.0, "Defense":4, "Resistance":7, "Attack Range":1,
			},
			"Terrain": {
				"G": 1.0, "F": 1.0, "W":99.0, "M": 2.0, "R": 0.5,
			},
			"Price":200,
		},
		"Armor":     {
			"AttackType":"Physical",
			"Description":"Melee unit with very high physical defense, but low magical resistance.",
			"Actions":{"Attack":True,"Heal":False,"Wait":True},
			"Stats": {
				"HP":20.5, "Move": 4.0, "Agility": 3.0, "Intelligence": 1.0, "Strength": 8.0, "Luck": 2.0, "Defense":8, "Resistance":1, "Attack Range":1,
			},
			"Terrain": {
				"G": 1.0, "F": 3.0, "W":99.0, "M":99.0, "R": 1.0,
			},
			"Price":300,
		},
		"Horseman":  {
			"AttackType":"Physical",
			"Description":"Mounted melee unit with high mobility.",
			"Actions":{"Attack":True,"Heal":False,"Wait":True},
			"Stats": {
				"HP":20.0, "Move": 7.0, "Agility": 8.0, "Intelligence": 3.0, "Strength": 6.0, "Luck": 6.0, "Defense":5, "Resistance":4, "Attack Range":1,
			},
			"Terrain": {
				"G": 1.0, "F": 3.0, "W":99.0, "M":99.0, "R": 0.5,
			},
			"Price":250,
		},
		"Flier":     {
			"AttackType":"Physical",
			"Description":"Flying melee unit, can move over any tile.  Low defense, especially to archers.",
			"Actions":{"Attack":True,"Heal":False,"Wait":True},
			"Stats": {
				"HP":10.0, "Move": 8.0, "Agility": 8.0, "Intelligence": 5.0, "Strength": 4.0, "Luck": 8.0, "Defense":3, "Resistance":6, "Attack Range":1,
			},
			"Terrain": {
				"G": 1.0, "F": 1.0, "W": 1.0, "M": 1.0, "R": 1.0,
			},
			"Price":200,
		},
	}

	# Leader Data
	data["Leaders"] = {
		"Sniper":{
			"Abilities":["Extra Range", "Evasion Aura"],
			"Description":"Ranged leader with very high damage output, but low armor."
		},
		"General":{
			"Abilities":["Defense Aura"],
			"Description":"Armored leader with very high physical defense.",
		},
		"Assassin":{
			"Abilities":["Steal", "Evasion Aura"],
			"Description":"Stealty melee unit with very high agility and mobility.",
		},
	}

	# Perk Data
	data["Perks"] = {
		"Extra Money":{
			"Tier":3,
			"Description":"Provides an extra 5% towards purchasing units.",
		},
		"Strong Arrows":{
			"Tier":2,
			"Description":"Provides an extra 10% damage for arrows.",
		},
		"Forest Fighter":{
			"Tier":1,
			"Description":"Provides an extra 15% damage when attacking from a Forest tile.",
		},
		"Mountain Fighter":{
			"Tier":1,
			"Description":"Provides an extra 15% damage when attacking from a Mountain tile.",
		},
	}

	# Map Data
	data["Map_Base"]  = "./Maps/v1_0/"
	data["Maps"]      = {
		"Grassland":     "allGrass.map",
		"Forest Pattern":"patternTree.map",
	}

	# Stat Data
	data["Stats"] = {
		"HP":           {
			"Description":"Number of health points.",
		},
		"Move":         {
			"Description":"Number of spaces the unit can move each turn.",
		},
		"Agility":      {
			"Description":"The speed of the unit.",
		},
		"Intelligence": {
			"Description":"The magical skill of the unit.",
		},
		"Strength":     {
			"Description":"The physical skill of the unit.",
		},
		"Luck":         {
			"Description":"How likely the unit is to deal critical damage.",
		},
		"Attack Range": {
			"Description":"The maximum distance at which the unit can hit a target.",
		},
		"Defense":      {
			"Description":"The unit's ability to prevent physical damage.",
		},
		"Resistance":   {
			"Description":"The unit's ability to prevent magical damage.",
		},
	}

	# Terrain Data
	data["Terrain"] = {
		"G":{
			"DisplayName":"Grass",
			"Description":"Basic terrain with no obstructions.",
		},
		"F":{
			"DisplayName":"Forest",
			"Description":"Wooded terrain.  Trees obstuct movement and ranged combat.",
		},
		"W":{
			"DisplayName":"Water",
			"Description":"Terrain covered entirely by water.  Movement impossible for land units.",
		},
		"M":{
			"DisplayName":"Mountain",
			"Description":"Mountainous terrain. Provides high vantage point for combat.",
		},
		"R":{
			"DisplayName":"Road",
			"Description":"Terrain with a path for easy movement.  Provides no additional cover.",
		},
	}

	return data

