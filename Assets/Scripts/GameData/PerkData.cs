using System.Collections.Generic;		// For dictionaries

// Holds game data for each unit
public class PerkData {

	public string name;
	public int tier;
	public string description;
	public string iconSpritePath;

	public PerkData(KeyValuePair<string, object> perk) {
		Dictionary<string, object> perkData = (Dictionary<string, object>)perk.Value;
		name = perk.Key;
		tier = int.Parse(perkData["Tier"].ToString());
		description = perkData["Description"].ToString();

		iconSpritePath = "Sprites/PerkIcons/DefaultTier" + tier; // Testing
	}

}
