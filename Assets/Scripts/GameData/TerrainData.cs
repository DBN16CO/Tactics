using System.Collections.Generic;		// For dictionaries

// Holds game data for each terrain
public class TerrainData {

	private string _name;
	private string _shortName;
	private string _description;
	private string _spritePath;

#region // Public properties
	public string Name {
		get{return _name;}
	}
	public string ShortName {
		get{return _shortName;}
	}
	public string Description {
		get{return _description;}
	}
	public string SpritePath {
		get{return _spritePath;}
	}
#endregion


	// Constructor when starting from IL Server call
	public TerrainData(KeyValuePair<string, object> terrain) {
		Dictionary<string, object> terrainData = (Dictionary<string, object>)terrain.Value;

		_name = Parse.String(terrainData["DisplayName"]);
		_shortName = terrain.Key;
		_description = Parse.String(terrainData["Description"]);
		_spritePath = "Sprites/Terrain/" + _name + GameData.Player.Preferences.GridOpacity;
	}

}
