//using UnityEngine;
using System.Collections.Generic;

public static class GameData {

	private static Dictionary<string, object> playerData;
	public static PlayerData Player;
	public static VersionData Version;

	private static List<object> matchData;
	private static List<MatchData> matches;
	public  static MatchData CurrentMatch;

	private static List<StatData> stats;
	private static Dictionary<string, object> statData;
	private static List<AbilityData> abilities;
	private static Dictionary<string, object> abilityData;
	private static List<ActionData> actions;
	private static Dictionary<string, object> actionData;
	private static List<PerkData> perks;
	private static Dictionary<string, object> perkData;
	private static List<UnitData> units;
	private static Dictionary<string, object> unitData;
	private static List<LeaderData> leaders;
	private static Dictionary<string, object> leaderData;
	private static List<TerrainData> terrains;
	private static Dictionary<string, object> terrainData;
	private static List<MapData> maps;
	private static Dictionary<string, object> mapData;

	private static int[][] terrainWeight;			// int map of terrain weights for each terrain and unit class

	// Sets player data
	public static void SetPlayerData(Dictionary<string, object> responseDict) {
		playerData = responseDict;
		Player = new PlayerData(playerData);
	}

	// Sets static game data
	public static void SetGameData(Dictionary<string, object> responseDict) {
		// Initiate private vars
		stats = new List<StatData>();
		abilities = new List<AbilityData>();
		actions = new List<ActionData>();
		perks = new List<PerkData>();
		units = new List<UnitData>();
		leaders = new List<LeaderData>();
		terrains = new List<TerrainData>();
		maps = new List<MapData>();
		// ------------------------------
		statData = (Dictionary<string, object>)responseDict["Stats"];
		abilityData = (Dictionary<string, object>)responseDict["Abilities"];
		actionData  = (Dictionary<string, object>)responseDict["Actions"];
		perkData = (Dictionary<string, object>)responseDict["Perks"];
		unitData = (Dictionary<string, object>)responseDict["Classes"];
		leaderData = (Dictionary<string, object>)responseDict["Leaders"];
		terrainData = (Dictionary<string, object>)responseDict["Terrain"];
		mapData = (Dictionary<string, object>)responseDict["Maps"];

		SetStatData(statData);
		SetAbilityData(abilityData);
		SetActionData(actionData);
		SetPerkData(perkData);
		SetUnitData(unitData);
		SetLeaderData(leaderData);
		SetTerrainData(terrainData);
		SetMapData(mapData);

		Version = new VersionData((Dictionary<string, object>)responseDict["Version"]);

		CreateWeightMap();
	}

#region // Set Static Data

	// Populates match data and creates callable list
	public static void SetMatchData(Dictionary<string, object> matchDict) {
		matches = new List<MatchData>();
		matches.Clear();

		if(matchDict["Games"].ToString() == "[]") {
			return;
		}
		matchData = Json.ToList(matchDict["Games"].ToString());
		foreach(object match in matchData) {
			matches.Add(new MatchData(Json.ToDict(match.ToString())));
			matches[matches.Count-1].MatchID = matches.Count-1;
		}
	}

	// Populates terrain data and creates callable list
	private static void SetTerrainData(Dictionary<string, object> terrainDict) {
		foreach(KeyValuePair<string, object> terrain in terrainDict) {
			terrains.Add(new TerrainData(terrain));
		}
	}

	// Populates stat data and creates callable list
	private static void SetStatData(Dictionary<string, object> statDict) {
		foreach(KeyValuePair<string, object> stat in statDict) {
			stats.Add(new StatData(stat, false));
		}
	}

	// Populates ability data and creates callable list
	private static void SetAbilityData(Dictionary<string, object> abilDict) {
		foreach(KeyValuePair<string, object> ability in abilDict) {
			abilities.Add(new AbilityData(ability));
		}
	}

	// Populates action data and creates callable list
	private static void SetActionData(Dictionary<string, object> actionDict) {
		foreach(KeyValuePair<string, object> action in actionDict) {
			actions.Add(new ActionData(action));
		}
	}

	// Populates perk data and creates callable list
	private static void SetPerkData(Dictionary<string, object> perkDict) {
		foreach(KeyValuePair<string, object> perk in perkDict) {
			perks.Add(new PerkData(perk));
		}
		perks.Sort((x,y) => x.tier.CompareTo(y.tier));
	}

	// Populates unit data and creates callable list
	private static void SetUnitData(Dictionary<string, object> unitDict) {
		foreach(KeyValuePair<string, object> unit in unitDict) {
			units.Add(new UnitData(unit));
		}
	}

	// Populates leader data and creates callable list
	private static void SetLeaderData(Dictionary<string, object> leaderDict) {
		foreach(KeyValuePair<string, object> leader in leaderDict) {
			leaders.Add(new LeaderData(leader));
		}
	}

	// Populates map data and creates callable list
	private static void SetMapData(Dictionary<string, object> mapDict) {
		foreach(KeyValuePair<string, object> map in mapDict) {
			maps.Add(new MapData(map));
		}
	}
#endregion

#region // Retrieve Static Data

	// Called to retrieve dynamic match data
	public static List<MatchData> GetMatches {
		get{return matches;}
	}

	// Called to retrieve static terrain data
	public static TerrainData GetTerrain(string shortNameKey) {
		return terrains.Find(x => x.shortName == shortNameKey);
	}
	public static List<TerrainData> GetTerrains {
		get{return terrains;}
	}

	// Called to retrieve static stat data
	public static StatData GetStat(string nameKey) {
		return stats.Find(x => x.name == nameKey);
	}
	public static List<StatData> GetStats {
		get{return stats;}
	}

	// Called to retrieve static ability data
	public static AbilityData GetAbility(string nameKey) {
		return abilities.Find(x => x.name == nameKey);
	}
	public static List<AbilityData> GetAbilities {
		get{return abilities;}
	}

	// Called to retrieve static action data
	public static ActionData GetAction(string nameKey) {
		return actions.Find(x => x.name == nameKey);
	}
	public static List<ActionData> GetActions {
		get{return actions;}
	}

	// Called to retrieve static perk data
	public static PerkData GetPerk(string nameKey) {
		return perks.Find(x => x.name == nameKey);
	}
	public static List<PerkData> GetPerks {
		get{return perks;}
	}

	// Called to retrieve static unit data
	public static UnitData GetUnit(string nameKey) {
		return units.Find(x => x.name == nameKey);
	}
	public static List<UnitData> GetUnits {
		get{return units;}
	}

	// Called to retrieve static leader data
	public static LeaderData GetLeader(string nameKey) {
		return leaders.Find(x => x.name == nameKey);
	}
	public static List<LeaderData> GetLeaders {
		get{return leaders;}
	}

	// Called to retrieve static map data
	public static MapData GetMap(string nameKey) {
		return maps.Find(x => x.name == nameKey);
	}
	public static List<MapData> GetMaps {
		get{return maps;}
	}

	// Called to easily get the terrain weight for a given terrain type and unit class
	// TerrainWeight("Mage", "Mountain") returns 3
	public static int TerrainWeight(string unitName, string terrainShortName) {
		return terrainWeight[units.FindIndex(x => x.name == unitName)][ terrains.FindIndex(y => y.shortName == terrainShortName)];
	}
#endregion

#region // Supporting Methods

	// Initialize the 2d array based on list counts, then extract weight from server response
	private static void CreateWeightMap(){
		terrainWeight = JaggedArray.CreateJaggedArray<int[][]>(units.Count, terrains.Count);

		foreach(UnitData unit in units) {
			foreach(TerrainData terrain in terrains) {
				Dictionary<string, object> unitDict = (Dictionary<string, object>)unitData[unit.name];
				Dictionary<string, object> terrainDict = (Dictionary<string, object>)unitDict["Terrain"];
				int unitTerrainWeight = int.Parse(terrainDict[terrain.shortName].ToString());
				terrainWeight[units.IndexOf(unit)][terrains.IndexOf(terrain)] = unitTerrainWeight;
			}
		}
	}
#endregion

}
