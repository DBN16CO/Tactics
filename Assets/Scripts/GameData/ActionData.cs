using System.Collections.Generic;		// For dictionaries

// Holds game data for each action
public class ActionData {

	private string _name;
	private string _description;

#region // Public properties
	public string Name {
		get{return _name;}
	}
	public string Description {
		get{return _description;}
	}
#endregion


	// Constructor when starting from IL Server call
	public ActionData(KeyValuePair<string, object> action) {
		_name = action.Key;
		_description = Parse.String(action.Value);
	}

}
