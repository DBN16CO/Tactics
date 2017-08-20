using System.Collections.Generic;		// For dictionaries

// Holds game data for each ability
public class AbilityData {

	private string _name;
	private string _description;

#region // Public properties
	public string Name {
		get{return _name;}
	}
	public string Description {
		get{return _description;}
	}
#endregion


	// Constructor when starting from IL Server call
	public AbilityData(KeyValuePair<string, object> ability) {
		_name = ability.Key;
		_description = ability.Value.ToString();
	}

	// Constructor for after IL Server call when we no longer have the IL dictionary
	public AbilityData(string ability) {
		_name = ability;
		_description = GameData.GetAbilities[_name].ToString();
	}

}
