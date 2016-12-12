using System.Collections.Generic;		// For dictionaries

// Class holding game data for each unit stat
public class StatData {

	public string name;
	public string description;

	public StatData(KeyValuePair<string, object> stat) {
		Dictionary<string, object> statData = (Dictionary<string, object>)stat.Value;
		name = stat.Key;
		description = statData["Description"].ToString();
	}

}
