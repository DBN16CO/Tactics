from Static.models import Version, Action, Class, Hero_Ability, Leader, Leader_Ability, Perk, Map, Stat, Unit_Stat, Terrain, Terrain_Unit_Movement
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
	ver = Version(name=data["Version"])
	ver.save()

	# Save the action data
	logging.info("Creating Action objects...")
	for actn in data["Actions"].keys():
		action = Action(name=actn, description=data["Actions"][actn], version_id=ver.id)
		action.save()

	# Save the class data
	logging.info("Creating Class objects...")
	for clss in data["Classes"].keys():
		class_inst = Class(name=clss, description=data["Classes"][clss], version_id=ver.id)
		class_inst.save()

	# Save the Hero Ability Data
	logging.info("Creating Hero Ability objects...")
	for hero_abil in data["Hero_Abils"].keys():
		ha_inst = Hero_Ability(name=hero_abil, description=data["Hero_Abils"][hero_abil], version_id=ver.id)
		ha_inst.save()

	# Save the Leader Data
	logging.info("Creating Leader objects...")
	for ldr in data["Leaders"]:
		ldr_inst =  Leader(name=ldr, description=data["Leaders"][ldr]["Description"], version_id=ver.id)
		ldr_inst.save()
		for abil in data["Leaders"][ldr]["Abilities"]:
			abil_id = Hero_Ability.objects.get(name=abil, version_id=ver.id).id
			ldr_abil_inst = Leader_Ability(leader_id=ldr_inst.id, ability_id=abil_id, version_id=ver.id)
			ldr_abil_inst.save()

	# Save the Perk Data
	logging.info("Creating Perk objects...")
	for prk in data["Perks"].keys():
		perk_inst = Perk(name=prk, description=data["Perks"][prk]["Description"], 
			tier=data["Perks"][prk]["Tier"], version_id=ver.id)
		perk_inst.save()

	# Save the Map Data
	logging.info("Creating Map objects...")
	for mp in data["Maps"].keys():
		map_inst = Map(name=mp, file_path=str(data["Map_Base"]) + data["Maps"][mp], version_id=ver.id)
		map_inst.save()

	# Save the Stat Data
	logging.info("Creating Stat objects...")
	for stt in data["Stats"].keys():
		stt_inst = Stat(name=stt, version_id=ver.id)
		stt_inst.save()
		for clss in data["Stats"][stt].keys():
			clss_id = Class.objects.get(name=clss, version_id=ver.id).id
			stt_unit_inst = Unit_Stat(stat_id=stt_inst.id, unit_id=clss_id, 
				value=data["Stats"][stt][clss], version_id=ver.id)
			stt_unit_inst.save()

	# Save the Terrain Data
	logging.info("Creating Terrain objects...")
	for ter in data["Terrain"].keys():
		ter_inst = Terrain(name=ter, shortname=data["Terrain"][ter]["Shortname"], version_id=ver.id)
		ter_inst.save()
		for clss in data["Terrain"][ter]["Units"].keys():
			clss_id = Class.objects.get(name=clss, version_id=ver.id).id
			ter_unt_mv_inst = Terrain_Unit_Movement(terrain_id=ter_inst.id, unit_id=clss_id, 
				move=data["Terrain"][ter]["Units"][clss], version_id=ver.id)
			ter_unt_mv_inst.save()

	return True

# Supplies all necessary setup data for version 1.0 of the game
def ver_1_0_static_data():
	data = {}

	# Version Data
	data["Version"] = "1.0"

	# Action Data
	data["Actions"] = {
		"Attack": "Deal damage to target unit.", 
		"Heal":   "Restore health to target allied unit.", 
		"Wait":   "End move without taking action."
	}

	# Class Data
	data["Classes"] = {
		"Archer":    "Ranged unit with low armor.  Good at defeating Fliers.", 
		"Swordsman": "Standard melee unit with average stats.", 
		"Mage":      "Magical ranged attacker with low defense.  Good at defeating armored units.", 
		"Rogue":     "Fast evasive melee unit.  Has low defense but high attack potential.", 
		"Armor":     "Melee unit with very high physical defense, but low magical resistance.", 
		"Horseman":  "Mounted melee unit with high mobility.", 
		"Flier":     "Flying melee unit, can move over any tile.  Low defense, especially to archers.",
	}

	# Hero Ability Data
	data["Hero_Abils"] = {
		"Extra Range":  "Increase the maximum range of nearby range attacks by 1.",
		"Steal":        "Provides nearby units the ability to steal items from the enemy.",
		"Defense Aura": "Increases the defense of nearby units.",
		"Evasion Aura": "Increases the chance your units will dodge an attack.",
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
	data["Terrain"] = {
		"Grass":{ 
			"Units":{
				"Archer":1.0, "Swordsman":1.0, "Mage":1.0, "Rogue":1.0, "Armor":1.0, "Horseman":1.0, "Flier":1.0,
			},
			"Shortname":"G",
		},
		"Forest":{
			"Units":{
				"Archer":2.0, "Swordsman":3.0, "Mage":2.0, "Rogue":1.0, "Armor":3.0, "Horseman":3.0, "Flier":1.0,
			},
			"Shortname":"F",
		},
		"Water":{
			"Units":{
				"Archer":99.0, "Swordsman":99.0, "Mage":99.0, "Rogue":99.0, "Armor":99.0, "Horseman":99.0, "Flier":1.0,
			},
			"Shortname":"W"
		},
		"Mountain":{
			"Units":{
				"Archer":4.0, "Swordsman":4.0, "Mage":3.0, "Rogue":2.0, "Armor":99.0, "Horseman":99.0, "Flier":1.0,
			},
			"Shortname":"M"
		},
		"Road":{
			"Units":{
				"Archer":1.0, "Swordsman":1.0, "Mage":1.0, "Rogue":0.5, "Armor":1.0, "Horseman":0.5, "Flier":1.0,
			},
			"Shortname":"R"
		}
	}

	return data

