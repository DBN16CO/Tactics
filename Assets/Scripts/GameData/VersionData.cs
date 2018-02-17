using System.Collections.Generic;		// For dictionaries

// Holds version specific data
public class VersionData {

	private int _maxFunds;
	private int _minUnits;
	private int _maxUnits;

#region // Public properties
	public int MaxFunds {
		get{return _maxFunds;}
	}
	public int MinUnits {
		get{return _minUnits;}
	}
	public int MaxUnits {
		get{return _maxUnits;}
	}
#endregion

	// Constructor when starting from IL Server call
	public VersionData(Dictionary<string, object> versionData) {
		_maxFunds = Parse.Int(versionData["Price_Max"]);
		_minUnits = Parse.Int(versionData["Unit_Min"]);
		_maxUnits = Parse.Int(versionData["Unit_Max"]);
	}

}
