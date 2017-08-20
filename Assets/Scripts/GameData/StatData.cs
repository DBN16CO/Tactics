using System.Collections.Generic;		// For dictionaries

// Holdss game data for each unit stat
public class StatData {

	private string 	_name;
	private string 	_description;	// Used in GameData.GetStats (i.e. for UI display)
	private int 	_value;			// Used in UnitData.GetStats (i.e. for in-game processing)

#region // Public properties
	public string Name {
		get{return _name;}
	}
	public string Description {
		get{return _description;}
	}
	public int Value {
		get{return _value;}
	}
#endregion


	// Constructor when starting from IL Server call
	public StatData(KeyValuePair<string, object> stat, bool forUnit) {
		_name = stat.Key;

		// For UI display (Name/Description)
		if(!forUnit) {
			Dictionary<string, object> statData = (Dictionary<string, object>)stat.Value;
			_description = statData["Description"].ToString();
		}
		// For Units (Name/Value)
		else {
			_value = int.Parse(stat.Value.ToString());
		}
	}

}
