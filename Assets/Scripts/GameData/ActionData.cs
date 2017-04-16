using System.Collections.Generic;		// For dictionaries

// Class holding game data for each action
public class ActionData {

	public string name;
	public string description;

	public ActionData(KeyValuePair<string, object> action) {
		Dictionary<string, object> actionData = (Dictionary<string, object>)action.Value;
		name = action.Key;
		description = action["Description"].ToString();
	}

}
