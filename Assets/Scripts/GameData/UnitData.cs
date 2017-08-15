using System;
using System.Collections.Generic;		// For dictionaries

// Holds game data for each unit
public class UnitData {

	public string name;
	public string description;
	public int price;
	public string spritePath;
	public Dictionary<string, bool> actions;

	private List<StatData> stats;

	public UnitData(KeyValuePair<string, object> unit) {
		Dictionary<string, object> unitData = (Dictionary<string, object>)unit.Value;
		name = unit.Key;
		description = unitData["Description"].ToString();
		price = Int32.Parse(unitData["Price"].ToString());
		spritePath = "Sprites/Units/axeman"; // Testing

		stats = new List<StatData>();
		foreach(KeyValuePair<string, object> stat in (Dictionary<string, object>)unitData["Stats"]) {
			stats.Add(new StatData(stat, true));
		}

		actions = new Dictionary<string, bool>();
		foreach(KeyValuePair<string, object> actn in (Dictionary<string, object>)unitData["Actions"]) {
			actions[actn.Key] = (bool)actn.Value;
		}
		
	}

	public StatData GetStat(string nameKey) {
		return stats.Find(x => x.name == nameKey);
	}

	public bool GetAction(string nameKey) {
		if(nameKey == null){
			return false;
		}

		bool canAct;
		actions.TryGetValue(nameKey, out canAct);

		return canAct;
	}

}
