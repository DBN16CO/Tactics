using System.Collections.Generic;		// For dictionaries

// Holds game data for each perk
public class PerkData {

	private string 	_name;
	private string 	_description;
	private int 	_tier;
	private string 	_iconSpritePath;

#region // Public properties
	public string Name {
		get{return _name;}
	}
	public string Description {
		get{return _description;}
	}
	public int Tier {
		get{return _tier;}
	}
	public string IconSpritePath {
		get{return _iconSpritePath;}
	}
#endregion


	// Constructor when starting from IL Server call
	public PerkData(KeyValuePair<string, object> perk) {
		Dictionary<string, object> perkData = (Dictionary<string, object>)perk.Value;

		_name = perk.Key;
		_tier = int.Parse(perkData["Tier"].ToString());
		_description = perkData["Description"].ToString();

		_iconSpritePath = "Sprites/PerkIcons/DefaultTier" + Tier; // Testing
	}

}
