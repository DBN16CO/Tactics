from Game.models import Unit
from Static.models import Class, Stat, Version

""" 
This file is used to store all methods helping with the processing of unit objects
"""

# Creates a unit of the given type for the given player
def createUnit(ownr, clss, vrsn):
	# Get necessary values to create unit
	clss_id = Class.objects.get(name=clss, version=vrsn).id
	hp_rem = Stat.objects.get(unit=clss_id, name='HP', version=vrsn).value

	# Create and save the unit
	retUnit = Unit(unit_class=clss_id, hp_remaining=hp_rem, owner=ownr, version=vrsn)
	retUnit.save()

	# Return the unit
	return retUnit