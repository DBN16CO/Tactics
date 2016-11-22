from Static.models import Version, Action, Class, Hero_Ability, Leader, Perk, Map, Stat, Terrain
import logging

# Will load the databse with all necessary static data based on the provided version name
def setup_static_db(version):
	cmd = {
		"1.0":ver_1_0_static_data
	}

	if not version in cmd:
		logging.error("Specified version does not exist.")
		return False

	# Load the data for the specified version
	data = cmd[version]()

	# Save the version data
	ver = Version(name=data["version"])
	ver.save()

	# Save the action data
	for actn in data["actions"].keys():
		action = Action(name=actn, description=data["actions"][actn], version_id=ver.id)
		action.save()

	# Save the class data
	for clss in data["classes"].keys():
		class_inst = Class(name=clss, description=data["classes"][clss], version_id=ver.id)
		class_inst.save()

	# Save the Hero Ability Data
	for hero_abil in data["hero_abils"].keys():
		ha_inst = Hero_Ability(name=hero_abil, description=data["hero_abils"][hero_abil], version_id=ver.id)
		ha_inst.save()

	# Save the Leader Data
	for ldr in data["leaders"]:
		for abil in data["leaders"][ldr]["Abilities"]:
			abil_id = Hero_Ability.objects.get(name=abil, version_id=ver.id).id
			ldr_inst = Leader(name=ldr, description=data["leaders"][ldr]["Description"], ability_id=abil_id, version_id=ver.id)
			ldr_inst.save()

	# Save the Perk Data
	for prk in data["perks"].keys():
		perk_inst = Perk(name=prk, description=data["perks"][prk]["Description"], 
			tier=data["perks"][prk]["Tier"], version_id=ver.id)
		perk_inst.save()

	# Save the Map Data
	for mp in data["maps"].keys():
		map_inst = Map(name=mp, file_path=str(data["map_base"]) + data["maps"][mp], version_id=ver.id)
		map_inst.save()

	# Save the Stat Data
	for stt in data["stats"].keys():
		for clss in data["stats"][stt].keys():
			clss_id = Class.objects.get(name=clss, version_id=ver.id).id
			stt_inst = Stat(name=stt, unit_id=clss_id, value=data["stats"][stt][clss], version_id=ver.id)
			stt_inst.save()

	# Save the Terrain Data
	for ter in data["terrain"].keys():
		for clss in data["terrain"][ter].keys():
			clss_id = Class.objects.get(name=clss, version_id=ver.id).id
			ter_inst = Terrain(name=ter, unit_id=clss_id, move=data["terrain"][ter][clss], version_id=ver.id)
			ter_inst.save()

	return True

# Supplies all necessary setup data for version 1.0 of the game
def ver_1_0_static_data():
	data = {}

	# Version Data
	data["version"] = "1.0"

	# Action Data
	data["actions"] = {
		"Attack": "Deal damage to target unit.", 
		"Heal":   "Restore health to target allied unit.", 
		"Wait":   "End move without taking action."
	}

	# Class Data
	data["classes"] = {
		"Archer":    "Ranged unit with low armor.  Good at defeating Fliers.", 
		"Swordsman": "Standard melee unit with average stats.", 
		"Mage":      "Magical ranged attacker with low defense.  Good at defeating armored units.", 
		"Rogue":     "Fast evasive melee unit.  Has low defense but high attack potential.", 
		"Armor":     "Melee unit with very high physical defense, but low magical resistance.", 
		"Horseman":  "Mounted melee unit with high mobility.", 
		"Flier":     "Flying melee unit, can move over any tile.  Low defense, especially to archers.",
	}

	# Hero Ability Data
	data["hero_abils"] = {
		"Extra Range":  "Increase the maximum range of nearby range attacks by 1.",
		"Steal":        "Provides nearby units the ability to steal items from the enemy.",
		"Defense Aura": "Increases the defense of nearby units.",
		"Evasion Aura": "Increases the chance your units will dodge an attack.",
	}

	# Leader Data
	data["leaders"] = {
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
	data["perks"] = {
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
	data["map_base"]  = "./Maps/v1_0/"
	data["maps"]      = {
		"Grassland":     "allGrass.map",
		"Forest Pattern":"patternTree.map",
	}

	# Stat Data
	data["stats"] = {
		"HP":           {
			"Archer":10.0, "Swordsman":15.0, "Mage":10.0, "Rogue":10.0, "Armor":20.5, "Horseman":20.0, "Flier":10.0},
		"Move":         {
			"Archer": 6.0, "Swordsman": 5.0, "Mage": 5.0, "Rogue": 6.0, "Armor": 4.0, "Horseman": 7.0, "Flier": 8.0},
		"Agility":      {
			"Archer": 8.5, "Swordsman": 6.0, "Mage": 5.0, "Rogue":10.5, "Armor": 3.0, "Horseman": 8.0, "Flier": 8.0},
		"Intelligence": {
			"Archer": 4.0, "Swordsman": 3.0, "Mage":10.5, "Rogue": 4.0, "Armor": 1.0, "Horseman": 3.0, "Flier": 5.0},
		"Strength":     {
			"Archer": 7.0, "Swordsman": 6.0, "Mage": 1.0, "Rogue": 3.0, "Armor": 8.0, "Horseman": 6.0, "Flier": 4.0},
		"Luck":         {
			"Archer": 7.0, "Swordsman": 5.0, "Mage": 7.0, "Rogue":11.0, "Armor": 2.0, "Horseman": 6.0, "Flier": 8.0},
	}

	# Terrain Data
	data["terrain"] = {
		"Grass":    
			{"Archer": 1.0, "Swordsman": 1.0, "Mage": 1.0, "Rogue": 1.0, "Armor": 1.0, "Horseman": 1.0, "Flier": 1.0},
		"Forest":   
			{"Archer": 2.0, "Swordsman": 3.0, "Mage": 2.0, "Rogue": 1.0, "Armor": 3.0, "Horseman": 3.0, "Flier": 1.0},
		"Water":    
			{"Archer":99.0, "Swordsman":99.0, "Mage":99.0, "Rogue":99.0, "Armor":99.0, "Horseman":99.0, "Flier": 1.0},
		"Mountain": 
			{"Archer": 4.0, "Swordsman": 4.0, "Mage": 3.0, "Rogue": 2.0, "Armor":99.0, "Horseman":99.0, "Flier": 1.0},
		"Road": 
			{"Archer": 1.0, "Swordsman": 1.0, "Mage": 1.0, "Rogue": 0.5, "Armor": 1.0, "Horseman": 0.5, "Flier": 1.0},
	}

	return data



	"""
	# Ensure that the data does not already exist
		if Version.objects.count() > 0:
			return

		# Create the version value in the database
		version   = "1.0"
		verObject = Version(name=version)
		verObject.save()
		ver_id    = verObject.id
		logging.debug("Version ID is " + str(ver_id))
		
		# Data for the tables
		actions    = ["Attack","Heal","Wait"]
		classes    = ["Archer", "Mage", "Healer", "Swordsman", "Horseman", "Flier", "Thief"]
		hero_abils = ["Extra Range", "Steal", "Regen Aura", ]
		leaders    = ["Sniper","General","Assassin"]
		perks      = ["Extra Money", "Strong Arrows", "Forest Fighter"]
		map_base   = "./Maps/"
		maps       = ["allGrass.map"]
		stats	   = ["HP","Move","Agility","Intelligence","Strength","Luck"]
		terrain    = ["Grass", "Forest", "Water", "Mountain"]

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
		for ldr in leaders:
			for abil_id in Hero_Ability.objects.values_list('pk', flat=True):
				leaderObject = Leader(name=ldr, ability_id=abil_id, version_id=ver_id)
				leaderObject.save()

		# Create the perks
		for prk in perks:
			perkObject = Perk(name=prk, version_id=ver_id)
			perkObject.save()

		# Create the maps
		for mp in maps:
			mapObject = Map(file_path=map_base + mp, version_id=ver_id)
			mapObject.save()

		# Create the stats
		counter=0
		for stt in stats:
			for unt in Class.objects.values_list('pk', flat=True):
				counter += 1
				statObject = Stat(name=stt, unit_id=unt, value=counter, version_id=ver_id)
				statObject.save()

		# Create the terrains
		counter = 0
		for trn in terrain:
			for clas in Class.objects.values_list('pk', flat=True):
				counter += 1
				terObject = Terrain(name=trn, unit_id=clas, move=counter, version_id=ver_id)
				terObject.save()
	"""
	