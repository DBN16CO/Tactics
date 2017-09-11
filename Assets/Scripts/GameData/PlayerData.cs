using System.Collections.Generic;		// For dictionaries

// Holds player data
public class PlayerData {

	private string 	_username;
	private string 	_email;
	private bool 	_verified;
	private int 	_level;
	private int 	_experience;

	private PreferenceData _preferences;

#region // Public properties
	public string Username {
		get{return _username;}
	}
	public string Email {
		get{return _email;}
	}
	public bool Verified {
		get{return _verified;}
	}
	public int Level {
		get{return _level;}
	}
	public int Experience {
		get{return _experience;}
	}
	public PreferenceData Preferences {
		get{return _preferences;}
	}
#endregion


	// Constructor when starting from IL Server call
	public PlayerData(Dictionary<string, object> player) {
		_username = Parse.String(player["Username"]);
		_email = Parse.String(player["Email"]);
		_verified = Parse.Bool(player["Verified"]);
		_level = Parse.Int(player["Level"]);
		_experience = Parse.Int(player["Experience"]);

		_preferences = new PreferenceData((Dictionary<string, object>)player["Preferences"]);
	}

}
