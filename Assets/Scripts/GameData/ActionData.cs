using System.Collections.Generic;		// For dictionaries

// Holds game data for each action
public class ActionData {

	public string name;
	public string description;

	public ActionData(KeyValuePair<string, object> action) {
		Dictionary<string, object> actionData = (Dictionary<string, object>)action.Value;
		name = action.Key;
		description = actionData["Description"].ToString();
	}

}
