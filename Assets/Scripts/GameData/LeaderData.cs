using System.Collections.Generic;		// For dictionaries

// Holds game data for each leader
public class LeaderData {

	private string _name;
	private string _description;
	private string _spritePath;

	private Dictionary<string, AbilityData> _abilities;

#region // Public properties
	public string Name {
		get{return _name;}
	}
	public string Description {
		get{return _description;}
	}
	public string SpritePath {
		get{return _spritePath;}
	}
	public Dictionary<string, AbilityData> Abilities {
		get{return _abilities;}
	}
#endregion


	// Constructor when starting from IL Server call
	public LeaderData(KeyValuePair<string, object> leader) {
		Dictionary<string, object> leaderData = (Dictionary<string, object>)leader.Value;

		_name = leader.Key;
		_description = Parse.String(leaderData["Description"]);
		_spritePath = "Sprites/Units/" + _name;

		// Populate abilities
		_abilities = new Dictionary<string, AbilityData>();
		foreach(string ability in Json.ToList(Parse.String(leaderData["Abilities"]))) {
			_abilities[ability] = new AbilityData(ability);
		}
	}

}
