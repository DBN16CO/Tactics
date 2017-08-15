using System.Collections.Generic;		// For dictionaries

// Holds game data for each ability
public class AbilityData {

	public string name;
	public string description;

	public AbilityData(KeyValuePair<string, object> ability) {
		name = ability.Key;
		description = ability.Value.ToString();
	}

	public AbilityData(string ability) {
		name = ability;
	}

}
