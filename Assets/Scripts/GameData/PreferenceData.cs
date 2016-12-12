using System.Collections.Generic;		// For dictionaries

public class PreferenceData {

	public string gridOpacity;

	public PreferenceData(Dictionary<string, object> preferences) {
		gridOpacity = preferences["Grid Opacity"].ToString();
	}

}
