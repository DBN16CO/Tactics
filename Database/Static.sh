#!/bin/bash

# This script is used to populate the static fields of the Database

version="1.0"
versionNum=1

# Version Database
sql="INSERT INTO \"Static_version\" (name) VALUES ('${version}');  "
echo $sql
sudo -u postgres psql -d tactics -c "$sql"

# Action
sql=""
actions=('Attack' 'Wait' 'Move' 'Heal')
for i in "${actions[@]}"
do
    sql="$sql INSERT INTO \"Static_action\" (name, version_id) VALUES ('${i}', ${versionNum});  "
done
echo $sql
sudo -u postgres psql -d tactics -c "$sql"

# Class
sql=""
classes=('Archer' 'Mage' 'Healer' 'Swordsman' 'Horseman' 'Flier' 'Thief')
for i in "${classes[@]}"
do
    sql="$sql INSERT INTO \"Static_class\" (name, version_id) VALUES ('${i}', ${versionNum});  "
done
echo $sql
sudo -u postgres psql -d tactics -c "$sql"

# Hero_Ability
sql=""
abilities=('Stealth' 'Command Aura' 'Extra Range')
for i in "${abilities[@]}"
do
    sql="$sql INSERT INTO \"Static_hero_ability\" (name, version_id) VALUES ('${i}', ${versionNum});  "
done
echo $sql
sudo -u postgres psql -d tactics -c "$sql"

# Leader
# Note: all heros get the ability 'Stealth' currently
sql=""
leaders=('Sniper' 'General' 'Assassin')
for i in "${leaders[@]}"
do
    sql="$sql INSERT INTO \"Static_leader\" (name, ability_id, version_id) VALUES ('${i}', 1, ${versionNum});  "
done
echo $sql
sudo -u postgres psql -d tactics -c "$sql"

# Perk
sql=""
perks=('Extra Funds' 'Strong Arrows' 'Quickness')
for i in "${perks[@]}"
do
    sql="$sql INSERT INTO \"Static_perk\" (name, version_id) VALUES ('${i}', ${versionNum});  "
done
echo $sql
sudo -u postgres psql -d tactics -c "$sql"

# Map
# ##TODO##

# Stat
sql=""
stats=('HP' 'Intelligence' 'Agility' 'Strength')
counter=0
unit_id=0
for unit in "${classes[@]}"
do
    let "unit_id++"
    for i in "${stats[@]}"
    do
        let "counter++"
        sql="$sql INSERT INTO \"Static_stat\" (name, unit_id, value, version_id) VALUES ('${i}', ${unit_id}, ${counter}, ${versionNum});  "
    done
done
echo $sql
sudo -u postgres psql -d tactics -c "$sql"