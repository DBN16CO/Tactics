//using UnityEngine;
//using System;
//using System.Collections;
using System.Collections.Generic;

public static class GameData {

	private static Dictionary<string, object> playerData;
	public static PlayerData Player;

	private static List<StatData> stats;
	private static Dictionary<string, object> statData;
	private static List<UnitData> units;
	private static Dictionary<string, object> unitData;
	private static List<TerrainData> terrains;
	private static Dictionary<string, object> terrainData;
	private static List<MapData> maps;
	private static Dictionary<string, object> mapData;

	private static float[][] terrainWeight;			// float map of terrain weights for each terrain and unit class

	// Sets player data
	public static void SetPlayerData(Dictionary<string, object> responseDict) {
		playerData = responseDict;
		Player = new PlayerData(playerData);
	}

	// Sets static game data
	public static void SetGameData(Dictionary<string, object> responseDict) {
		// Initiate private vars
		stats = new List<StatData>();
		units = new List<UnitData>();
		terrains = new List<TerrainData>();
		maps = new List<MapData>();
		// ------------------------------
		statData = (Dictionary<string, object>)responseDict["Stats"];
		unitData = (Dictionary<string, object>)responseDict["Classes"];
		terrainData = (Dictionary<string, object>)responseDict["Terrain"];
		mapData = (Dictionary<string, object>)responseDict["Maps"];

		SetStatData(statData);
		SetUnitData(unitData);
		SetTerrainData(terrainData);
		SetMapData(mapData);

		CreateWeightMap();
	}

#region // Set Static Data

	// Populates terrain data and creates callable list
	private static void SetTerrainData(Dictionary<string, object> terrainDict) {
		foreach(KeyValuePair<string, object> terrain in terrainDict) {
			//terrains.Add(new TerrainData((Dictionary<string, object>)terrainDict[terrain.Key]));
			terrains.Add(new TerrainData(terrain));
		}
	}

	// Populates stat data and creates callable list
	private static void SetStatData(Dictionary<string, object> statDict) {
		foreach(KeyValuePair<string, object> stat in statDict) {
			stats.Add(new StatData(stat));
		}
	}

	// Populates unit data and creates callable list
	private static void SetUnitData(Dictionary<string, object> unitDict) {
		foreach(KeyValuePair<string, object> unit in unitDict) {
			units.Add(new UnitData(unit));
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

	// Called to retrieve static terrain data
	public static TerrainData Terrains(string shortNameKey) {
		return terrains.Find(x => x.shortName == shortNameKey);
	}

	// Called to retrieve static stat data
	public static StatData Stats(string nameKey) {
		return stats.Find(x => x.name == nameKey);
	}

	// Called to retrieve static unit data
	public static UnitData Units(string nameKey) {
		return units.Find(x => x.name == nameKey);
	}

	// Called to retrieve static map data
	public static MapData Maps(string nameKey) {
		return maps.Find(x => x.name == nameKey);
	}

	// Called to easily get the terrain weight for a given terrain type and unit class
	// TerrainWeight("Mage", "Mountain") returns 3f
	public static float TerrainWeight(string unitName, string terrainShortName) {
		return terrainWeight[units.FindIndex(x => x.name == unitName)][terrains.FindIndex(y => y.shortName == terrainShortName)];
	}
#endregion

#region // Supporting Methods

	// Initialize the 2d array based on list counts, then extract weight from server response
	private static void CreateWeightMap(){
		terrainWeight = new float[units.Count][];
		for(int cnt = 0; cnt < terrainWeight.Length; cnt++) {
			terrainWeight[cnt] = new float[terrains.Count];
		}
		foreach(UnitData unit in units) {
			foreach(TerrainData terrain in terrains) {
				Dictionary<string, object> unitDict = (Dictionary<string, object>)unitData[unit.name];
				Dictionary<string, object> terrainDict = (Dictionary<string, object>)unitDict["Terrain"];
				float unitTerrainWeight = float.Parse(terrainDict[terrain.shortName].ToString());
				terrainWeight[units.IndexOf(unit)][terrains.IndexOf(terrain)] = unitTerrainWeight;
			}
		}
		/*for(int x = 0; x < units.Count; x++) {
			string ret = units[x].name + ": ";
			for(int y = 0; y < terrains.Count; y++) {
				ret += terrains[y].shortName + ": " + terrainWeight[x][y].ToString() + ", ";
			}
			UnityEngine.Debug.Log(ret);
		}*/
	}
#endregion

}
