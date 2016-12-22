using System.Collections.Generic;		// For dictionaries

// Class holding game data for each action
public class ActionData {

	public string name;
	public string description;

	public ActionData(KeyValuePair<string, object> action) {
		name = action.Key;
		description = action.Value.ToString();
	}

}
