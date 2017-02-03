using System;
using System.Collections.Generic;		// For dictionaries

// Class holding game data for each unit
public class UnitData {

	public string name;
	public string description;
	public int price;
	public string spritePath;

	private List<StatData> stats;

	public UnitData(KeyValuePair<string, object> unit) {
		Dictionary<string, object> unitData = (Dictionary<string, object>)unit.Value;
		name = unit.Key;
		description = unitData["Description"].ToString();
		price = Int32.Parse(unitData["Price"].ToString());
		spritePath = "Sprites/Units/axeman";

		stats = new List<StatData>();
		foreach(KeyValuePair<string, object> stat in (Dictionary<string, object>)unitData["Stats"]) {
			stats.Add(new StatData(stat, true));
		}
	}

	public StatData GetStat(string nameKey) {
		return stats.Find(x => x.name == nameKey);
	}

}
