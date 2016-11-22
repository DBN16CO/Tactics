using UnityEngine;
using System;
using System.Text;
using System.Collections.Generic;
using Common.Cryptography;
using System.Security.Cryptography;
using System.Text.RegularExpressions;

public static class Server {

	private const float SERVER_TIMEOUT = 5f;

	//private static bool _timedOut;

	public static void Connect() {
		Communication.Connect(new Uri("ws://localhost:8000"));
	}

	/*public static IEnumerator Timeout(int timeout) {
		Server._timedOut = false;
		Debug.Log("Trying to connect to server...");
		int seconds = 0;
		while(seconds < timeout) {
			seconds++;
			yield return new WaitForSeconds(1f);
			Debug.Log("Waited " + seconds + " of " + Server.SERVER_TIMEOUT + " seconds...");
			if(seconds == timeout) {
				Server._timedOut = true;
				break;
			}
		}
	}*/

	public static bool Login(string username, string pw) {
		var request = new Dictionary<string, object>();
		request["Command"] 	= "LGN";
		request["username"]	= username;
		request["pw"]		= pw;
		Communication.SendString(Json.ToString(request));
		string response = null;
		while(response == null) {
			response = Communication.RecvString();
		}
		bool success = (bool)Json.ToDict(response)["Success"];
		if(success) {
			string _loginToken = Json.ToDict(response)["Token"].ToString();
			string _encryptedToken = AES.Encrypt(_loginToken, GeneratePasswordHash());
			PlayerPrefs.SetString("session", _encryptedToken);
			Debug.Log("user '" + username + "' logged in with token: " + _loginToken);
		}
		return success;
	}

	public static bool RetryLogin() {
		var request = new Dictionary<string, object>();
		string _encryptedToken = PlayerPrefs.GetString("session");
		string _loginToken = AES.Decrypt(_encryptedToken, GeneratePasswordHash());
		request["Command"] 	= "LGN";
		request["token"] 	= _loginToken;
		Communication.SendString(Json.ToString(request));
		string response = null;
		while(response == null) {
			response = Communication.RecvString();
		}
		bool success = (bool)Json.ToDict(response)["Success"];
		if(success) {
			Debug.Log("user re-logged in with token: " + _loginToken);
		}else {
			Debug.Log("error logging user in with existing token");
		}
		return success;
	}

	public static bool CreateUser(string username, string pw, string email) {
		var request = new Dictionary<string, object>();
		request["Command"] 	= "CU";
		request["username"]	= username;
		request["pw"]		= pw;
		request["email"]	= email;
		Communication.SendString(Json.ToString(request));
		string response = null;
		while (response == null) {
			response = Communication.RecvString();
		}
		bool success = (bool)Json.ToDict(response)["Success"];
		Debug.Log("user '" + username + "' created: " + success);
		return success;
	}

	public static string GeneratePasswordHash() {
	    MD5CryptoServiceProvider md5 = new MD5CryptoServiceProvider();
	    byte[] tmpSource;
	    byte[] tmpHash;

	    string source = SystemInfo.deviceUniqueIdentifier;
		Regex regX = new Regex(@"([<>""'%;()&])");
    	source = regX.Replace(source, "");

	    tmpSource = ASCIIEncoding.ASCII.GetBytes(source);
	    tmpHash = md5.ComputeHash(tmpSource);

	    StringBuilder sOutput = new StringBuilder(tmpHash.Length);
	    for (int i = 0; i < tmpHash.Length; i++) {
	        sOutput.Append(tmpHash[i].ToString("X2"));  // X2 formats to hexadecimal
	    }
	    return sOutput.ToString();
	}
}
