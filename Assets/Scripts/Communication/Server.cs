using UnityEngine;
using System;
using System.Linq;
using System.Threading;
using System.Text;
using System.Collections.Generic;
using Common.Cryptography;
using System.Security.Cryptography;
using System.Text.RegularExpressions;

// This class contains all of the Server call functions
public static class Server {

	public static bool inQueue;
	private static string url = "ws://tactics-dev.ddns.net:8443";
	//private static string url = "ws://localhost:8000";
	//private static string url = ""ws://tactics-production.herokuapp.com/""


	public static void Connect() {
		Communication.Connect(new Uri(url));
	}

	public static void Disconnect() {
		Communication.Close();
	}

	private static Dictionary<string, object> SendCommand(Dictionary<string, object> request) {
		string[] noLoginReqCommands = {"LGN", "CU"};

		// Verify the websocket is still connected and try to reconnect if it isn't
		if (!Communication.IsConnected()){
			Communication.Close();
			Communication.Connect(new Uri(url));
		}

		// Failed to reconnect with the server
		if (!Communication.IsConnected()){
			return null;
		}

		// Send the request
		Communication.SendString(Json.ToString(request));

		// Wait for the response
		string strResponse = null;
		Dictionary<string, object> response = null;

		int retryCount = 0;
		const int maxRetries = 20;
		while(strResponse == null && retryCount < maxRetries) {
			strResponse = Communication.RecvString();
			if (strResponse != null){
				response = Json.ToDict(strResponse);
				if (!noLoginReqCommands.All(request["Command"].ToString().Contains) && IsUnauthenticated(response)){
					// Server says we are not logged in, re-authenticate
					RetryLogin();
					strResponse = null;
					response = null;
					Communication.SendString(Json.ToString(request));
				}
			}

			if (strResponse == null){
				retryCount++;
				Thread.Sleep(100);
			}
		}

		if (response == null){
			return null;
		}

		bool success = (bool)response["Success"];
		if(!success) {
			Debug.Log("Request (" + request["Command"] + ") Failed");
		}

		return response;
	}

	public static bool InitialLoad() {
		var request = new Dictionary<string, object>();
		request["Command"] = "IL";
		Dictionary<string, object> response = SendCommand(request);

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

		Dictionary<string, object> response = SendCommand(request);

		if (response == null){
			return false;
		}

		bool success = (bool)response["Success"];
		if(success) {
			string _loginToken = response["Token"].ToString();
			string _encryptedToken = AES.Encrypt(_loginToken, GenerateAESKey());
			PlayerPrefs.SetString("session", _encryptedToken);
			PlayerPrefs.Save();
			Debug.Log("user '" + username + "' logged in with token: " + _loginToken);
		}

		return success;
	}

	private static bool IsUnauthenticated(Dictionary<string, object> response){
		bool success = (bool)response["Success"];
		if (!success){
			string error = response["Error"].ToString();
			if (error.Contains("User is not authenticated")){
				Debug.Log("User is not authenticated, retry logging in.");
				return true;
			}
		}

		return false;
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
		var request = new Dictionary<string, object>();
		request["Command"] = "GUI";
		Dictionary<string, object> response = SendCommand(request);

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

		Dictionary<string, object> response = SendCommand(request);

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

		Dictionary<string, object> response = SendCommand(request);

		if (response == null){
			return false;
		}

		bool success = (bool)response["Success"];
		Debug.Log("user '" + username + "' created: " + success);

		return success;
	}

	// Used to query active games for user
	public static bool QueryGames() {
		var request = new Dictionary<string, object>();
		request["Command"] = "GQU";
		Dictionary<string, object> response = SendCommand(request);

		bool success = (bool)response["Success"];

		return success;
	}

	// Used to set selected team in database
	public static bool SetTeam(string leader, string ability, List<string> units, List<string> perks) {
		var request = new Dictionary<string, object>();
		request["Command"] = "ST";
		request["Leader"] = leader;
		request["Ability"] = ability;
		request["Units"] = units;
		request["Perks"] = perks;

		Dictionary<string, object> response = SendCommand(request);

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
		Dictionary<string, object> response = SendCommand(request);

		bool success = (bool)response["Success"];

		return success;
	}

	// Called to cancel ranked match queue
	public static bool CancelQueue() {
		var request = new Dictionary<string, object>();
		request["Command"] = "CS";
		Dictionary<string, object> response = SendCommand(request);

		if (response == null){
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
