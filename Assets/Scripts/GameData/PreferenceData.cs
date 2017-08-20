using System.Collections.Generic;		// For dictionaries

// Holds player preference data
public class PreferenceData {

	private string _gridOpacity;

#region // Public properties
	public string GridOpacity {
		get{return _gridOpacity;}
	}
#endregion


	// Constructor when starting from IL Server call
	public PreferenceData(Dictionary<string, object> preferences) {
		_gridOpacity = preferences["Grid Opacity"].ToString();
	}

}
