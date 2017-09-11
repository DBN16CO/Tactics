﻿using System.Collections.Generic;		// For dictionaries

// Holds game data for each unit
public class UnitData {

	private string 	_name;
	private string 	_description;
	private int 	_price;
	private string 	_spritePath;

	private Dictionary<string, bool> 		_actions;
	private Dictionary<string, StatData> 	_stats;

#region // Public properties
	public string Name {
		get{return _name;}
	}
	public string Description {
		get{return _description;}
	}
	public int Price {
		get{return _price;}
	}
	public string SpritePath {
		get{return _spritePath;}
	}
	public StatData GetStat(string stat) {
		return _stats[stat];
	}
#endregion


	// Constructor when starting from IL Server call
	public UnitData(KeyValuePair<string, object> unit) {
		Dictionary<string, object> unitData = (Dictionary<string, object>)unit.Value;

		_name = unit.Key;
		_description = Parse.String(unitData["Description"]);
		_price = Parse.Int(unitData["Price"]);
		_spritePath = "Sprites/Units/" + _name;

		// Populate stats
		_stats = new Dictionary<string, StatData>();
		foreach(KeyValuePair<string, object> stat in (Dictionary<string, object>)unitData["Stats"]) {
			_stats[stat.Key] = new StatData(stat, true);
		}

		// Populate actions
		_actions = new Dictionary<string, bool>();
		foreach(KeyValuePair<string, object> actn in (Dictionary<string, object>)unitData["Actions"]) {
			_actions[actn.Key] = Parse.Bool(actn.Value);
		}
		
	}

	// Returns if the unit can perform the specified action
	public bool Can(string nameKey) {
		bool canAct;
		_actions.TryGetValue(nameKey, out canAct);
		return canAct;
	}

}
