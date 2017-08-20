using System.Collections.Generic;		// For dictionaries

// Holds version specific data
public class VersionData {

	private int _maxFunds;

#region // Public properties
	public int MaxFunds {
		get{return _maxFunds;}
	}
#endregion


	// Constructor when starting from IL Server call
	public VersionData(Dictionary<string, object> versionData) {
		_maxFunds = int.Parse(versionData["Price_Max"].ToString());
	}

}
