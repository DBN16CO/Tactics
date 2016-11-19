using UnityEngine;
using System;
using System.Collections.Generic;

public static class Server {

	public static void Connect() {
		Communication.Connect(new Uri("ws://localhost:8000"));
	}

	public static bool CreateUser(string username, string pw, string email) {
		var request = new Dictionary<string, object>();
		request["Command"] 	= "CU";
		request["username"]	= username;
		request["pw"]		= pw;
		request["email"]	= email;
		Communication.SendString (Json.ToString(request));
		string response = null;
		while (response == null) {
			response = Communication.RecvString ();
		}
		bool success = (bool)Json.ToDict(response)["Success"];
		Debug.Log("user '" + username + "' created: " + success);
		return success;
	}
}
