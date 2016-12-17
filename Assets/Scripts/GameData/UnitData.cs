using System.Collections.Generic;		// For dictionaries

// Class holding game data for each unit
public class UnitData {

	public string name;
	public string description;
	public string spritePath;

	private List<StatData> stats;

	public UnitData(KeyValuePair<string, object> unit) {
		Dictionary<string, object> unitData = (Dictionary<string, object>)unit.Value;
		name = unit.Key;
		description = unitData["Description"].ToString();

		stats = new List<StatData>();
		foreach(KeyValuePair<string, object> stat in (Dictionary<string, object>)unitData["Stats"]) {
			stats.Add(new StatData(stat, true));
		}
	}

	public StatData Stats(string nameKey) {
		return stats.Find(x => x.name == nameKey);
	}

}
