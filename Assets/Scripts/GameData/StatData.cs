using System.Collections.Generic;		// For dictionaries

// Class holding game data for each unit stat
public class StatData {

	public string name;
	public string description;
	public float value;

	public StatData(KeyValuePair<string, object> stat, bool forUnit) {
		name = stat.Key;
		if(!forUnit) {
			Dictionary<string, object> statData = (Dictionary<string, object>)stat.Value;
			description = statData["Description"].ToString();
		}else {
			value = float.Parse(stat.Value.ToString());
		}
	}

}
