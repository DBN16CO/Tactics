using System.Collections.Generic;		// For dictionaries

// Holds player preference data
public class PreferenceData {

	public string GridOpacity;

	public PreferenceData(Dictionary<string, object> preferences) {
		GridOpacity = preferences["Grid Opacity"].ToString();
	}

}
