using UnityEngine;
using System;
using System.Text;
using System.Collections.Generic;
using Common.Cryptography;
using System.Security.Cryptography;
using System.Text.RegularExpressions;

// This class contains all of the Server call functions
public static class Server {

	public static bool inQueue;


	public static void Connect() {
		// Local host -----------
		//Communication.Connect(new Uri("ws://localhost:8000"));
		// Raspberry Pi ---------
		Communication.Connect(new Uri("ws://tactics-dev.ddns.net:8443"));
		// Heroku ---------------
		//Communication.Connect(new Uri("ws://tactics-production.herokuapp.com/"));
	}

	public static bool InitialLoad() {
		// Create the request, set data to pass, and send it
		var request = new Dictionary<string, object>();
		request["Command"] = "IL";
		Communication.SendString(Json.ToString(request));
		// Wait for the response, then parse
		string strResponse = null;
		while(strResponse == null) {
			strResponse = Communication.RecvString();
		}
		var response = Json.ToDict(strResponse);
		bool success = (bool)response["Success"];
		if(success) {
			//Debug.Log(strResponse);
			GameData.SetGameData(response);
		}
		return success;
	}

	// Used to login to server with username and password
	public static bool Login(string username, string pw) {
		// Create the request, set data to pass, and send it
		var request = new Dictionary<string, object>();
		request["Command"] 	= "LGN";
		request["username"]	= username;
		request["pw"]		= pw;
		Communication.SendString(Json.ToString(request));
		// Wait for the response, then parse
		string strResponse = null;
		while(strResponse == null) {
			strResponse = Communication.RecvString();
		}
		var response = Json.ToDict(strResponse);
		// If login successful, encrypt and store session token
		bool success = (bool)response["Success"];
		if(success) {
			string _loginToken = response["Token"].ToString();
			string _encryptedToken = AES.Encrypt(_loginToken, GenerateAESKey());
			PlayerPrefs.SetString("session", _encryptedToken);
			PlayerPrefs.Save();
			inQueue = false;
			Debug.Log("user '" + username + "' logged in with token: " + _loginToken);
		}
		return success;
	}

	// Used to login to server with cached session token
	public static bool RetryLogin() {
		// Create the request, decrypt session token, and send it
		var request = new Dictionary<string, object>();
		string _encryptedToken = PlayerPrefs.GetString("session");
		string _loginToken = AES.Decrypt(_encryptedToken, GenerateAESKey());
		request["Command"] 	= "LGN";
		request["token"] 	= _loginToken;
		Communication.SendString(Json.ToString(request));
		// Wait for the response, then parse
		string strResponse = null;
		while(strResponse == null) {
			strResponse = Communication.RecvString();
		}
		var response = Json.ToDict(strResponse);
		// Error Handling
		bool success = (bool)response["Success"];
		if(success) {
			Debug.Log("user re-logged in with token: " + _loginToken);
		}else {
			Debug.Log("error logging user in with existing token");
			PlayerPrefs.DeleteKey("session");
			PlayerPrefs.Save();
		}
		return success;
	}

	// Used to get user preferences
	public static bool GetUserInfo() {
		// Create the request
		var request = new Dictionary<string, object>();
		request["Command"] = "GUI";
		Communication.SendString(Json.ToString(request));
		// Wait for the response, then parse
		string strResponse = null;
		while(strResponse == null) {
			strResponse = Communication.RecvString();
		}
		var response = Json.ToDict(strResponse);
		// Error Handling
		bool success = (bool)response["Success"];
		if(success) {
			//Debug.Log(strResponse);
			GameData.SetPlayerData(response);
		}
		return success;
	}

	// Used to logout of the server
	public static bool Logout() {
		// Create the request, decrypt session token, and send it
		var request = new Dictionary<string, object>();
		request["Command"] = "LGO";
		Communication.SendString(Json.ToString(request));
		// Wait for the response, then parse
		string strResponse = null;
		while(strResponse == null) {
			strResponse = Communication.RecvString();
		}
		var response = Json.ToDict(strResponse);
		// If successful, delete cached token
		bool success = (bool)response["Success"];
		if(success) {
			Debug.Log("User logged out");
			PlayerPrefs.DeleteKey("session");
			PlayerPrefs.Save();
		}
		return success;
	}

	// Used to create a user in the database
	public static bool CreateUser(string username, string pw, string email) {
		// Create the request, set the data, and send
		var request = new Dictionary<string, object>();
		request["Command"] 	= "CU";
		request["username"]	= username;
		request["pw"]		= pw;
		request["email"]	= email;
		Communication.SendString(Json.ToString(request));
		// Wait for the response, then parse
		string strResponse = null;
		while(strResponse == null) {
			strResponse = Communication.RecvString();
		}
		var response = Json.ToDict(strResponse);
		// Error Handling
		bool success = (bool)response["Success"];
		Debug.Log("user '" + username + "' created: " + success);
		return success;
	}

	// Used to query active games for user
	public static bool QueryGames() {
		// Create the request, set the data, and send
		var request = new Dictionary<string, object>();
		request["Command"] = "QGU";
		Communication.SendString(Json.ToString(request));
		// Wait for the response, then parse
		string strResponse = null;
		while(strResponse == null) {
			strResponse = Communication.RecvString();
		}
		var response = Json.ToDict(strResponse);
		// Error handling
		bool success = (bool)response["Success"];
		if(success) {
			inQueue = true;
		}
		return success;
	}

	// Used to set selected team in database
	public static bool SetTeam(string leader, string ability, List<string> units, List<string> perks) {
		// Create the request, set the data, and send
		var request = new Dictionary<string, object>();
		request["Command"] = "ST";
		request["Leader"] = leader;
		request["Ability"] = ability;
		request["Units"] = units;
		request["Perks"] = perks;
		Communication.SendString(Json.ToString(request));
		// Wait for the response, then parse
		string strResponse = null;
		while(strResponse == null) {
			strResponse = Communication.RecvString();
		}
		var response = Json.ToDict(strResponse);
		// Error handling
		bool success = (bool)response["Success"];
		return success;
	}

	// Called to find ranked match after team is set
	public static bool FindMatch() {
		if(inQueue) {
			// Create the request, set the data, and send
			var request = new Dictionary<string, object>();
			request["Command"] = "FM";
			Communication.SendString(Json.ToString(request));
			// Wait for the response, then parse
			string strResponse = null;
			while(strResponse == null) {
				strResponse = Communication.RecvString();
			}
			var response = Json.ToDict(strResponse);
			// Error handling
			bool success = (bool)response["Success"];
			if(success) {
				inQueue = true;
			}
			return success;
		}
		Debug.Log("User is already in queue");
		return false;
	}

	// Called to cancel ranked match queue
	public static bool CancelQueue() {
		if(!inQueue) {
			// Create the request, set the data, and send
			var request = new Dictionary<string, object>();
			request["Command"] = "CS";
			Communication.SendString(Json.ToString(request));
			// Wait for the response, then parse
			string strResponse = null;
			while(strResponse == null) {
				strResponse = Communication.RecvString();
			}
			var response = Json.ToDict(strResponse);
			// Error handling
			bool success = (bool)response["Success"];
			if(success) {
				inQueue = false;
			}
			return success;
		}
		Debug.Log("User does not have a queue to cancel");
		return false;
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
