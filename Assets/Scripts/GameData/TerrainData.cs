using System.Collections.Generic;		// For dictionaries

// Class holding game data for each terrain
public class TerrainData {

	public string shortName;
	public string name;
	public string description;
	public string spritePath;

	public TerrainData(KeyValuePair<string, object> terrain) {
		Dictionary<string, object> terrainData = (Dictionary<string, object>)terrain.Value;
		shortName = terrain.Key;
		name = terrainData["DisplayName"].ToString();
		if(terrainData.ContainsKey("Description")) {
			description = terrainData["Description"].ToString();
		}
		spritePath = "Sprites/Terrain/" + name + GameController.GridAlpha;
	}

}
