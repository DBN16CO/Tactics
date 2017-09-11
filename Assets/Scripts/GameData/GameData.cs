using System.Collections.Generic;		// For dictionaries

// Starting reference point for all static game data
public static class GameData {

	private static PlayerData 	_player;						// Reference to the logged in user
	private static MatchData 	_currentMatch;					// Reference to the actively open match
	private static VersionData 	_version;						// Reference to version specific data

	private static Dictionary<int, MatchData> 		_matches;	// List of matches brought back from QGU
	private static Dictionary<string, MapData> 		_maps;		// List of static map data
	private static Dictionary<string, TerrainData> 	_terrains;	// List of static terrain data
	private static Dictionary<string, UnitData> 	_units;		// List of static unit data
	private static Dictionary<string, ActionData> 	_actions;	// List of static action data
	private static Dictionary<string, StatData> 	_stats;		// List of static stat data
	private static Dictionary<string, LeaderData> 	_leaders;	// List of static leader data
	private static Dictionary<string, AbilityData> 	_abilities;	// List of static ability data
	private static Dictionary<string, PerkData> 	_perks;		// List of static perk data
	
	private static Dictionary<string, Dictionary<string, int>> _terrainWeight;	// Terrain weight of movement for each unit

#region // Public properties
	public static PlayerData Player {
		get{return _player;}
		set{_player = value;}
	}
	public static MatchData CurrentMatch {
		get{return _currentMatch;} 
		set{_currentMatch = value;}
	}
	public static VersionData Version {
		get{return _version;} 
		set{_version = value;}
	}
#endregion


	// Sets static game data
	public static void SetGameData(Dictionary<string, object> gameData) {
		// Initiate dictionaries
		_maps 		= new Dictionary<string, MapData>();
		_terrains 	= new Dictionary<string, TerrainData>();
		_units 		= new Dictionary<string, UnitData>();
		_actions 	= new Dictionary<string, ActionData>();
		_stats 		= new Dictionary<string, StatData>();
		_leaders 	= new Dictionary<string, LeaderData>();
		_abilities 	= new Dictionary<string, AbilityData>();
		_perks 		= new Dictionary<string, PerkData>();
		
		// Map IL Data to temp dictionaries
		Dictionary<string, object> mapData 		= (Dictionary<string, object>)gameData["Maps"];
		Dictionary<string, object> terrainData 	= (Dictionary<string, object>)gameData["Terrain"];
		Dictionary<string, object> unitData 	= (Dictionary<string, object>)gameData["Classes"];
		Dictionary<string, object> actionData  	= (Dictionary<string, object>)gameData["Actions"];
		Dictionary<string, object> statData 	= (Dictionary<string, object>)gameData["Stats"];
		Dictionary<string, object> leaderData 	= (Dictionary<string, object>)gameData["Leaders"];
		Dictionary<string, object> abilityData 	= (Dictionary<string, object>)gameData["Abilities"];
		Dictionary<string, object> perkData 	= (Dictionary<string, object>)gameData["Perks"];

		// Set dictionaries (ORDER MATTERS - i.e. Ability must come before Leader)
		SetMapData(mapData);
		SetTerrainData(terrainData);
		SetUnitData(unitData);
		SetActionData(actionData);
		SetStatData(statData);
		SetAbilityData(abilityData);
		SetLeaderData(leaderData);
		SetPerkData(perkData);

		// Other
		_version = new VersionData((Dictionary<string, object>)gameData["Version"]);
		CreateWeightMap(unitData);
	}

#region // Set Static Data

	// Sets player data
	public static void SetPlayerData(Dictionary<string, object> playerData) {
		_player = (playerData != null)? new PlayerData(playerData) : null;
	}

	// Populates match data and creates callable list
	public static void SetMatchData(Dictionary<string, object> matchDict) {
		// Return if no matches
		if(matchDict["Games"].ToString() == "[]") {
			return;
		}

		_matches = new Dictionary<int, MatchData>();
		int key;
		List<object> matchData = Json.ToList(Parse.String(matchDict["Games"]));
		Dictionary<string, object> matchDataAsDict;

		// Populate matches
		foreach(object match in matchData) {
			matchDataAsDict = Json.ToDict(Parse.String(match));
			key = Parse.Int(matchDataAsDict["ID"]);
			_matches[key] = new MatchData(matchDataAsDict);
		}
	}

	// Populate map data into static list
	private static void SetMapData(Dictionary<string, object> mapDict) {
		foreach(KeyValuePair<string, object> map in mapDict) {
			_maps[map.Key] = new MapData(map);
		}
	}

	// Populate terrain data into static list
	private static void SetTerrainData(Dictionary<string, object> terrainDict) {
		foreach(KeyValuePair<string, object> terrain in terrainDict) {
			_terrains[terrain.Key] = new TerrainData(terrain);
		}
	}

	// Populate unit data into static list
	private static void SetUnitData(Dictionary<string, object> unitDict) {
		foreach(KeyValuePair<string, object> unit in unitDict) {
			_units[unit.Key] = new UnitData(unit);
		}
	}

	// Populate action data into static list
	private static void SetActionData(Dictionary<string, object> actionDict) {
		foreach(KeyValuePair<string, object> action in actionDict) {
			_actions[action.Key] = new ActionData(action);
		}
	}

	// Populate stat data into static list
	private static void SetStatData(Dictionary<string, object> statDict) {
		foreach(KeyValuePair<string, object> stat in statDict) {
			_stats[stat.Key] = new StatData(stat, false);
		}
	}

	// Populate ability data into static list
	private static void SetAbilityData(Dictionary<string, object> abilDict) {
		foreach(KeyValuePair<string, object> ability in abilDict) {
			_abilities[ability.Key] = new AbilityData(ability);
		}
	}

	// Populate leader data into static list
	private static void SetLeaderData(Dictionary<string, object> leaderDict) {
		foreach(KeyValuePair<string, object> leader in leaderDict) {
			_leaders[leader.Key] = new LeaderData(leader);
		}
	}

	// Populate perk data into static list
	private static void SetPerkData(Dictionary<string, object> perkDict) {
		foreach(KeyValuePair<string, object> perk in perkDict) {
			_perks[perk.Key] = new PerkData(perk);
		}
	}
#endregion

#region // Retrieve Static Data

	// Called to retrieve dynamic match data
	public static Dictionary<int, MatchData> Matches {
		get{return _matches;}
	}
	public static MatchData GetMatch(int match) {
		return _matches[match];
	}

	// Called to retrieve static terrain data
	public static TerrainData GetTerrain(string terrain) {
		return _terrains[terrain];
	}

	// Called to retrieve static stat data
	public static StatData GetStat(string stat) {
		return _stats[stat];
	}

	// Called to retrieve static ability data
	public static AbilityData GetAbility(string ability) {
		return _abilities[ability];
	}

	// Called to retrieve static action data
	public static ActionData GetAction(string action) {
		return _actions[action];
	}

	// Called to retrieve static perk data
	public static Dictionary<string, PerkData> Perks {
		get{return _perks;}
	}
	public static PerkData GetPerk(string perk) {
		return _perks[perk];
	}

	// Called to retrieve static unit data
	public static Dictionary<string, UnitData> Units {
		get{return _units;}
	}
	public static UnitData GetUnit(string unit) {
		return _units[unit];
	}

	// Called to retrieve static leader data
	public static Dictionary<string, LeaderData> Leaders {
		get{return _leaders;}
	}
	public static LeaderData GetLeader(string leader) {
		return _leaders[leader];
	}

	// Called to retrieve static map data
	public static MapData GetMap(string map) {
		return _maps[map];
	}

	// Called to easily get the terrain weight for a given terrain type and unit class
	// TerrainWeight("Mage", "Mountain") returns 3
	public static int TerrainWeight(string unitName, string terrainShortName) {
		return _terrainWeight[_units[unitName].Name][_terrains[terrainShortName].ShortName];
	}
#endregion

#region // Supporting Methods

	// Initialize dictionary of dictionaries referring to terrain weight for each unit
	private static void CreateWeightMap(Dictionary<string, object> unitsDict){
		_terrainWeight = new Dictionary<string, Dictionary<string, int>>();
		Dictionary<string, object> unitDict;
		Dictionary<string, object> unitTerrainDict;
		
		// Loop through units
		foreach(KeyValuePair<string, object> unit in unitsDict) {
			unitDict = (Dictionary<string, object>)unit.Value;
			unitTerrainDict = (Dictionary<string, object>)unitDict["Terrain"];
			_terrainWeight[unit.Key] = new Dictionary<string, int>();
			
			// Loop through terrain weights for current unit
			foreach(KeyValuePair<string, object> terrain in unitTerrainDict) {
				int unitTerrainWeight = Parse.Int(terrain.Value);
				_terrainWeight[unit.Key][terrain.Key] = unitTerrainWeight;
			}
		}
	}

	// Update a specific game's data based on a received end turn message
	public static void UpdateETGameData(int matchID){
		if(!_matches.ContainsKey(matchID)){
			return;
		}
		_matches[matchID].StartTurn();
	}

	// Update a specific game's data based on a received take action message
	public static void UpdateTAGameData(int matchID, Dictionary<string, object> unit, Dictionary<string, object> target){
		// The 'Unit' from user 2's perspective is the enemy
		int enemy_id = Parse.Int(unit["ID"]);
		UnitInfo enemy = _matches[matchID].EnemyUnits[enemy_id];
		int enemyX  = Parse.Int(unit["NewX"]);
		int enemyY  = Parse.Int(unit["NewY"]);

		// The 'Target' from user 2's perspective is his/her unit
		if(target != null){
			int allied_id = Parse.Int(target["ID"]);
			UnitInfo ally = _matches[matchID].AlliedUnits[allied_id];
			int allyHP = Parse.Int(target["NewHP"]);

			// HP can only change for actions that involved a target
			int enemyHP = Parse.Int(unit["NewHP"]);

			ally.UpdateInfo(allyHP);
			enemy.UpdateInfo(enemyHP, enemyX, enemyY);
		}else {
			enemy.UpdateInfo(newX: enemyX, newY: enemyY);
		}
		enemy.SetActed(true);
	}
#endregion

}
