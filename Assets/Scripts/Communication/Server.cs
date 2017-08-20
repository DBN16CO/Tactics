﻿using UnityEngine;						// For Unity's PlayerPrefs
using System.Collections.Generic;		// For dictionaries
using Common.Cryptography;				// For AES encryption

// Holds all of the Server call functions related to gameplay
public static class Server {

	// Used to get user info and preferences
	public static bool GetUserInfo() {
		var request = new Dictionary<string, object>();
		request["Command"] = "GUI";
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

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
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		if (response == null){
			return false;
		}

		bool success = (bool)response["Success"];
		if (success){
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
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		if (response == null){
			return false;
		}

		bool success = (bool)response["Success"];
		return success;
	}

	// Used to query active games for user
	public static Dictionary<string, object> QueryGames() {
		var request = new Dictionary<string, object>();
		request["Command"] = "QGU";
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

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
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

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
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

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
			unitDict["ID"] 		= unit.Info.ID;
			unitDict["Name"] 	= unit.Info.Name;
			unitDict["X"]		= unit.Info.X;
			unitDict["Y"]		= unit.Info.Y;
			unitsDict.Add(unitDict);
		}
		request["Units"] = unitsDict;
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

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
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		if (response == null){
			return false;
		}
		bool success = (bool)response["Success"];
		return success;
	}

	// Called to have a unit take a move action on the game map
	public static bool TakeNonTargetAction(Unit unit, string action, int X = -1, int Y = -1) {
		var request = new Dictionary<string, object>();
		request["Command"] = "TA";
		request["Game"] = GameData.CurrentMatch.Name;
		request["Action"] = action;
		request["Unit"] = unit.Info.ID;

		// Wait at current position if optional params not passed in
		request["X"] = (X == -1)? unit.Info.X : X;
		request["Y"] = (Y == -1)? unit.Info.Y : Y;
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		if(response == null) {
			return false;
		}
		bool success = (bool)response["Success"];
		return success;
	}

	// Called to have a unit take an attack/heal action on the game map
	public static bool TakeTargetAction(Unit unit, string action, int targetID, out Dictionary<string, object> unitDict, out Dictionary<string, object> targetDict, int X = -1, int Y = -1) {
		var request = new Dictionary<string, object>();
		request["Command"] = "TA";
		request["Game"] = GameData.CurrentMatch.Name;
		request["Action"] = action;
		request["Unit"] = unit.Info.ID;

		// Wait at current position if optional params not passed in
		request["X"] = (X == -1)? unit.Info.X : X;
		request["Y"] = (Y == -1)? unit.Info.Y : Y;
		request["Target"] = targetID;
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		unitDict = null;
		targetDict = null;
		if(response == null) {
			return false;
		}
		bool success = (bool)response["Success"];
		if(success) {
			// Set out params
			unitDict = (Dictionary<string, object>)response["Unit"];
			targetDict = (Dictionary<string, object>)response["Target"];
		}
		return success;
	}

	// Called to end a player's turn
	public static bool EndTurn() {
		var request = new Dictionary<string, object>();
		request["Command"] = "ET";
		request["Game"] = GameData.CurrentMatch.Name;
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		if(response == null) {
			return false;
		}
		bool success = (bool)response["Success"];
		return success;
	}

	// Loads static game data on login
	public static bool InitialLoad() {
		var request = new Dictionary<string, object>();
		request["Command"] = "IL";
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		if (response == null){
			return false;
		}

		bool success = (bool)response["Success"];
		if(success) {
			GameData.SetGameData(response);
		}
		return success;
	}

	// Used to login to server with username and password
	public static bool Login(string username, string pw) {
		var request = new Dictionary<string, object>();
		request["Command"] 	= "LGN";
		request["username"]	= username;
		request["pw"]		= pw;
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		if (response == null){
			return false;
		}

		bool success = (bool)response["Success"];
		if(success) {
			string _loginToken = response["Token"].ToString();
			string _encryptedToken = AES.Encrypt(_loginToken, CommunicationManager.GenerateAESKey());
			PlayerPrefs.SetString("session", _encryptedToken);
			PlayerPrefs.Save();
		}
		return success;
	}
}
