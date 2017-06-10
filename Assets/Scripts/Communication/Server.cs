using UnityEngine;
using System;
using System.Linq;
using System.Threading;
using System.Text;
using System.Collections.Generic;

// This class contains all of the Server call functions
public static class Server {

	public static bool inQueue;
	private static string url = "ws://tactics-dev.ddns.net:8443";
	//private static string url = "ws://localhost:8000";
	//private static string url = ""ws://tactics-production.herokuapp.com/""

	

	// Used to get user preferences
	public static bool GetUserInfo() {
		var request = new Dictionary<string, object>();
		request["Command"] = "GUI";
		Dictionary<string, object> response = CommunicationManager.Request(request);

		if (response == null){
			return false;
		}

		bool success = (bool)response["Success"];
		if(success) {
			GameData.SetPlayerData(response);
		}

		return success;
	}

	// Used to logout of the server
	public static bool Logout() {
		var request = new Dictionary<string, object>();
		request["Command"] = "LGO";

		Dictionary<string, object> response = CommunicationManager.Request(request);

		if (response == null){
			return false;
		}

		bool success = (bool)response["Success"];
		if (success){
			Debug.Log("User logged out");
			PlayerPrefs.DeleteKey("session");
			PlayerPrefs.Save();
		}

		return success;
	}

	// Used to create a user in the database
	public static bool CreateUser(string username, string pw, string email) {
		var request = new Dictionary<string, object>();
		request["Command"] 	= "CU";
		request["username"]	= username;
		request["pw"]		= pw;
		request["email"]	= email;

		Dictionary<string, object> response = CommunicationManager.Request(request);

		if (response == null){
			return false;
		}

		bool success = (bool)response["Success"];
		Debug.Log("user '" + username + "' created: " + success);

		return success;
	}

	// Used to query active games for user
	public static Dictionary<string, object> QueryGames() {
		var request = new Dictionary<string, object>();
		request["Command"] = "QGU";
		Dictionary<string, object> response = CommunicationManager.Request(request);
		bool success = (bool)response["Success"];
		if(success) {
			GameData.SetMatchData(response);
		}
		return response;
	}

	// Used to set selected team in database
	public static bool SetTeam(string leader, string ability, List<string> units, List<string> perks) {
		var request = new Dictionary<string, object>();
		request["Command"] = "ST";
		request["Leader"] = leader;
		request["Ability"] = ability;
		request["Units"] = units;
		request["Perks"] = perks;

		Dictionary<string, object> response = CommunicationManager.Request(request);
		if (response == null){
			return false;
		}
		bool success = (bool)response["Success"];
		return success;
	}

	// Called to find ranked match after team is set
	public static bool FindMatch() {
		var request = new Dictionary<string, object>();
		request["Command"] = "FM";
		Dictionary<string, object> response = CommunicationManager.Request(request);

		bool success = (bool)response["Success"];

		return success;
	}

	// Called to send placed unit info to database
	public static bool PlaceUnits(MatchData match) {
		var request = new Dictionary<string, object>();
		request["Command"] = "PU";
		request["Game"] = match.Name;

		List<Dictionary<string, object>> unitsDict = new List<Dictionary<string, object>>();
		foreach(Unit unit in GameController.Units) {
			var unitDict = new Dictionary<string, object>();
			MatchUnit unitInfo = unit.Info;
			unitDict["ID"] 		= unitInfo.ID;
			unitDict["Name"] 	= unitInfo.Name;
			unitDict["X"]		= unitInfo.X;
			unitDict["Y"]		= unitInfo.Y;
			unitsDict.Add(unitDict);
		}
		request["Units"] = unitsDict;

		Dictionary<string, object> response = CommunicationManager.Request(request);
		if (response == null){
			return false;
		}
		bool success = (bool)response["Success"];
		return success;
	}

	// Called to cancel ranked match queue
	public static bool CancelQueue() {
		var request = new Dictionary<string, object>();
		request["Command"] = "CS";

		Dictionary<string, object> response = CommunicationManager.Request(request);
		if (response == null){
			return false;
		}
		bool success = (bool)response["Success"];
		return success;
	}

	// Called to have a unit take an action on the game map (attacking/moving/etc.)
	public static bool TakeAction(MatchUnit unit, string action, int X = -1, int Y = -1, int targetID = -1) {
		var request = new Dictionary<string, object>();
		request["Command"] = "TA";
		request["Game"] = GameData.CurrentMatch.Name;
		request["Action"] = action;
		request["Unit"] = unit.ID;
		request["X"] = (X == -1)? unit.X : X;
		request["Y"] = (Y == -1)? unit.Y : Y;
		if(targetID != -1) {
			request["Target"] = targetID;
		}

		Dictionary<string, object> response = CommunicationManager.Request(request);
		if(response == null) {
			return false;
		}
		bool success = (bool)response["Success"];
		return success;
	}

	//Called to end a player's turn
	public static bool EndTurn() {
		var request = new Dictionary<string, object>();
		request["Command"] = "ET";
		request["Game"] = GameData.CurrentMatch.Name;

		Dictionary<string, object> response = CommunicationManager.Request(request);
		if(response == null) {
			return false;
		}
		bool success = (bool)response["Success"];
		return success;
	}

	// Generates the key to use for AES encryption
	public static string GenerateAESKey() {
	    MD5CryptoServiceProvider md5 = new MD5CryptoServiceProvider();
	    byte[] tmpSource;
	    byte[] tmpHash;

	    // Get unique identifier for device
	    string source = SystemInfo.deviceUniqueIdentifier;
		Regex regX = new Regex(@"([<>""'%;()&])");
    	source = regX.Replace(source, "");

    	// Convert to byte[] and compute MD5 hash
	    tmpSource = ASCIIEncoding.ASCII.GetBytes(source);
	    tmpHash = md5.ComputeHash(tmpSource);

	    // Convert to hexadecimal to ensure valid characters
	    StringBuilder sOutput = new StringBuilder(tmpHash.Length);
	    for (int i = 0; i < tmpHash.Length; i++) {
	        sOutput.Append(tmpHash[i].ToString("X2"));  // X2 formats to hexadecimal
	    }
	    return sOutput.ToString();
	}
}
