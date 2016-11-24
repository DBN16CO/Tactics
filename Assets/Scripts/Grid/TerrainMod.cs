using UnityEngine;
using System;

public static class TerrainMod {

	public static float[][] terrainWeight;			// float map of terrain weights for each terrain and unit class

	// Called on app load to generate the terrain weight map
	public static void CreateWeightMap(){
		// Initialize the 2d array based on enum lengths
		terrainWeight = new float[Enum.GetValues(typeof(UnitTypes)).Length][];
		for(int cnt = 0; cnt < terrainWeight.Length; cnt++) {
			terrainWeight[cnt] = new float[Enum.GetValues(typeof(TerrainTypes)).Length];
		}

		// Testing - will get these values from the server
		// Larger numbers mean more weight. Values of 0 means impassable
		terrainWeight[(int)UnitTypes.Warrior][(int)TerrainTypes.Grass 	] 	= 1f;
		terrainWeight[(int)UnitTypes.Warrior][(int)TerrainTypes.Forest	] 	= 1.5f;
		terrainWeight[(int)UnitTypes.Warrior][(int)TerrainTypes.Road	] 	= 0.5f;
		terrainWeight[(int)UnitTypes.Warrior][(int)TerrainTypes.Mountain]	= 0f;

		terrainWeight[(int)UnitTypes.Gryphon][(int)TerrainTypes.Grass 	] 	= 1f;
		terrainWeight[(int)UnitTypes.Gryphon][(int)TerrainTypes.Forest	] 	= 1f;
		terrainWeight[(int)UnitTypes.Gryphon][(int)TerrainTypes.Road	] 	= 1f;
		terrainWeight[(int)UnitTypes.Gryphon][(int)TerrainTypes.Mountain]	= 2f;
	}

	// Called to easily get the terrain weight for a given terrain type and unit class
	public static float TerrainWeight(string unitType, string terrainType) {
		return terrainWeight[(int)Enum.Parse(typeof(UnitTypes), unitType)][(int)Enum.Parse(typeof(TerrainTypes), terrainType)];
	}


}

// List of terrain types
public enum TerrainTypes {
    Grass,
    Forest,
    Road,
    Mountain
}

// List of unit types
public enum UnitTypes {
    Warrior,
    Gryphon
}
