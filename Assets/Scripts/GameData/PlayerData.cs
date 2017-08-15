using System.Collections.Generic;		// For dictionaries

// Holds player data
public class PlayerData {

	public string 	Username;
	public string 	Email;
	public bool 	Verified;
	public int 		Level;
	public int 		Experience;

	public PreferenceData Preferences;

	// Constructor
	public PlayerData(Dictionary<string, object> player) {
		Username = player["Username"].ToString();
		Email = player["Email"].ToString();
		Verified = (bool)player["Verified"];
		Level = int.Parse(player["Level"].ToString());
		Experience = int.Parse(player["Experience"].ToString());

		Preferences = new PreferenceData((Dictionary<string, object>)player["Preferences"]);
	}

}
