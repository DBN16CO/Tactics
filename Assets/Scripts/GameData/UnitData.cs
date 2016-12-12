using System.Collections.Generic;		// For dictionaries

// Class holding game data for each unit
public class UnitData {

	public string name;
	public string description;
	public string spritePath;

	public UnitData(KeyValuePair<string, object> unit) {
		Dictionary<string, object> unitData = (Dictionary<string, object>)unit.Value;
		name = unit.Key;
		description = unitData["Description"].ToString();
	}

}
