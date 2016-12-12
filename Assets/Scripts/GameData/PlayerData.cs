using System.Collections.Generic;		// For dictionaries

// Class holding game data for each Player
public class PlayerData {

	public string username;
	public string email;
	public bool verified;
	public uint level;
	public uint experience;

	public PreferenceData Preferences;

	public PlayerData(Dictionary<string, object> player) {
		username = player["Username"].ToString();
		email = player["Email"].ToString();
		verified = (bool)player["Verified"];
		level = uint.Parse(player["Level"].ToString());
		experience = uint.Parse(player["Experience"].ToString());

		Preferences = new PreferenceData((Dictionary<string, object>)player["Preferences"]);
	}

}
