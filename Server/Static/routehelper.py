"""
This file will handle all routed methods managing static data
All methods must follow the following standards:\n
Inputs - they will all take in only one input: the JSON data\n
Outputs - they will pass back a formatted JSON response object
which will detail the success or failure of the command
as well as any other necessary information regarding the command.
"""
import Static.statichelper

def getAllStaticData(data):
	"""
	Called when a user initially opens the app and needs to load all the data from the Static database
	Command: IL (Initial Load)

	:type  data: Dictionary
	:param data: No input information is needed, so simply an empty dictionary suffices

	:rtype: 	 Dictionary
	:return: 	 A JSON object noting the success of the method call.\n
				 Example if Successful:\n
				 {\n
				 	"Success":True,\n
				 	"Version":{\n
				 		"Price_Max":1000,\n
				 		"Unit_Count":8\n
				 	},\n
				 	"Abilities":{\n
				 		"Extra Range":  "Increase the maximum range of nearby range attacks by 1.",\n
				 		<Next Ability>,\n
				 	},\n
				 	"Actions":{\n
				 		"Attack": {\n
				 			"Description":"Deal damage to target unit."\n
				 		},\n
						<Next Action>,\n
					},\n
				 	"Classes":{\n
						"Archer":    {\n
							"Description":"Ranged unit with low armor.  Good at defeating Fliers.",\n
							"Stats": {\n
								"HP":10.0, "Move": 6.0, "Agility": 8.5, "Intelligence": 4.0, "Strength": 7.0, "Luck": 7.0, "Attack Range":2,\n
							},\n
							"Terrain": {\n
								"G": 1.0, "F": 2.0, "W":99.0, "M": 4.0, "R": 1.0,\n
							},\n
							"Price":150,\n
						},\n
						<Next Class>,\n
				 	},\n
					"Leaders":{\n
						"Sniper":{\n
							"Abilities":["Extra Range", "Evasion Aura"],\n
							"Description":"Ranged leader with very high damage output, but low armor."\n
						},\n
						<Next Leader>,\n
					},\n
					"Perks":{\n
						"Extra Money":{\n
							"Tier":3,\n
							"Description":"Provides an extra 5% towards purchasing units.",\n
						},\n
						<Next Perk>,\n
					},\n
					"Maps":{\n
						"Grassland":0,G 0,G 0,G 0,G 0,G 0,G 0,G 0,Gn0,G 0,G 0,G 0,G 0,G 0,G 0,G 0,G...\n
						<Next Map>,\n
					},\n
					"Stats":{\n
						"HP":{\n
							"Description":"Number of health points.",\n
						},\n
						<Next Stat>,\n
					},\n
					"Terrain":{\n
						"G":{\n
							"DisplayName":"Grass",\n
							"Description":"Basic terrain with no obstructions.",\n
						},\n
						<Next Terrain>,\n
					}\n
				 }\n
				 Notes:\n
				 - For map, each token has a,b where a=Can unit start there, b=Terrain shortname, n=Next row\n
				 - The Keys in terrain are their 'shortname' which must match up with the map's 'b' value\n
				 If Unsuccessful:\n
				 	{"Successful":False,\n
				 	 "Error":"<Error Message"}\n
				 Notes:\n
				 	- The error message provided should be of an acceptable form such that
				 	  errors can be directly displayed for the user.

	"""

	#TODO Determine if user needs other version's static data
	response = Static.statichelper.getAllStaticDataIL()

	response["Success"] = True if not "Error" in response else False

	return response

def modifyCustomMap(data):
	"""
	Called when a user wants to create or edit a custom map.

	:type  data: Dictionary
	:param data: The necessary input information to process the command, should
	             be of the following format:\n
	             {\n
	             	"name":"<map name>",\n
	             	"map":"0,G 0,G 0,G 0,G 0,G 0,G 0,G 0,Gn0,G 0,G 0,G 0,G 0,G 0,G 0,G 0,G..."\n
	             }\n
	"""
	username = data["session_username"]
	user = Users.objects.filter(username=username).first()

	if "name" not in data:
		error = "No map name was provided."
		return formJsonResult(error)

	if "map" not in data:
		error = "No map data was provided."
		return formJsonResult(error)

	map_name = data["name"]
	map_data = data["map"]

	response = Static.statichelper.modifyCustomMap(user, map_name, map_data)

	return response
