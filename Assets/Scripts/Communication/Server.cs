using Common.Cryptography;
using System.Collections.Generic;		// For dictionaries
using UnityEngine;						// For Unity's PlayerPrefs

// Holds all of the Server call functions related to gameplay
public static class Server {

	public static Dictionary<string, object> GetResponse(string rid){
		return CommunicationManager.GetResponse(rid);
	}

	/**
	 * The server requests in in the section that follows are associated with logging into the application,
	 * and requesting all necessary data from the server to fully initialize the game.
	 */
	// Used to create a user in the database
	public static void CreateUser(string username, string pw, string email, ParentController pc){
		Dictionary<string, object> request = new Dictionary<string, object>();
		request["username"]	= username;
		request["pw"]		= pw;
		request["email"]	= email;

		BasicServerRequest(RequestType.CU, pc, request);
	}

	// Used to get user info and preferences
	public static void GetUserInfo(ParentController pc) {
		BasicServerRequest(RequestType.GUI, pc);
	}

	// Loads static game data on login
	public static void InitialLoad(ParentController pc) {
		BasicServerRequest(RequestType.IL, pc);
	}

	// Used to login to server with username and password
	public static void Login(string username, string pw, ParentController pc) {
		Dictionary<string, object> request = new Dictionary<string, object>();
		request["username"]	= username;
		request["pw"]		= pw;

		BasicServerRequest(RequestType.LGN, pc, request);
	}

	// Used to login to server with cached session token
	public static void TokenLogin(ParentController pc){
		string _encryptedToken = PlayerPrefs.GetString("session");
		string _loginToken = AES.Decrypt(_encryptedToken, CommunicationManager.GenerateAESKey());

		// Create the request, decrypt session token, and send it
		Dictionary<string, object> request = new Dictionary<string, object>();
		request["token"] = _loginToken;

		BasicServerRequest(RequestType.LGN, pc, request);
	}

	// Used to query active games for user
	public static void QueryGames(ParentController pc, int filterGameID = -1) {
		Dictionary<string, object> request = null;

		if(filterGameID != -1){
			request = new Dictionary<string, object>();
			Dictionary<string, object> filtDict = new Dictionary<string, object>();
			filtDict.Add("Game_ID", filterGameID);
			request["Filters"] = filtDict;
		}

		BasicServerRequest(RequestType.QGU, pc, request);
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

	// Used to set selected team in database
	public static Dictionary<string, object> SetTeam(string leader, string ability, List<string> units, List<string> perks) {
		var request = new Dictionary<string, object>();
		request["Command"] = "ST";
		request["Leader"] = leader;
		request["Ability"] = ability;
		request["Units"] = units;
		request["Perks"] = perks;
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		if (response == null){
			response = CommunicationManager.CreateInternalErrorResponse();
		}
		return response;
	}

	// Called to find ranked match after team is set
	public static Dictionary<string, object> FindMatch() {
		var request = new Dictionary<string, object>();
		request["Command"] = "FM";
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		if (response == null){
			response = CommunicationManager.CreateInternalErrorResponse();
		}
		return response;
	}

	// Called to send placed unit info to database
	public static Dictionary<string, object> PlaceUnits(MatchData match) {
		var request = new Dictionary<string, object>();
		request["Command"] = "PU";
		request["Game"] = match.Name;

		List<Dictionary<string, object>> unitsDict = new List<Dictionary<string, object>>();
		foreach(Unit unit in GameController.Units) {
			var unitDict = new Dictionary<string, object>();
			unitDict["ID"] 		= unit.ID;
			unitDict["Name"] 	= unit.UnitName;
			unitDict["X"]		= unit.X;
			unitDict["Y"]		= unit.Y;
			unitsDict.Add(unitDict);
		}
		request["Units"] = unitsDict;
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		if (response == null){
			response = CommunicationManager.CreateInternalErrorResponse();
		}
		return response;
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
	public static Dictionary<string, object> TakeNonTargetAction(Unit unit, string action, int X = -1, int Y = -1) {
		var request = new Dictionary<string, object>();
		request["Command"] = "TA";
		request["Game"] = GameData.CurrentMatch.Name;
		request["Action"] = action;
		request["Unit"] = unit.ID;

		// Wait at current position if optional params not passed in
		request["X"] = (X == -1)? unit.X : X;
		request["Y"] = (Y == -1)? unit.Y : Y;
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		if(response == null) {
			response = CommunicationManager.CreateInternalErrorResponse();
		}
		return response;
	}

	// Called to have a unit take an attack/heal action on the game map
	public static Dictionary<string, object> TakeTargetAction(Unit unit, string action, int targetID, int X = -1, int Y = -1){
		var request = new Dictionary<string, object>();
		request["Command"] = "TA";
		request["Game"] = GameData.CurrentMatch.Name;
		request["Action"] = action;
		request["Unit"] = unit.ID;

		// Wait at current position if optional params not passed in
		request["X"] = (X == -1)? unit.X : X;
		request["Y"] = (Y == -1)? unit.Y : Y;
		request["Target"] = targetID;
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		if(response == null) {
			response = CommunicationManager.CreateInternalErrorResponse();
		}
		return response;
	}

	// Called to end a player's turn
	public static Dictionary<string, object> EndTurn() {
		var request = new Dictionary<string, object>();
		request["Command"] = "ET";
		request["Game"] = GameData.CurrentMatch.Name;
		Dictionary<string, object> response = CommunicationManager.RequestAndGetResponse(request);

		if(response == null) {
			response = CommunicationManager.CreateInternalErrorResponse();
		}
		return response;
	}

	// Sends the FCM Registration Information to the server
	public static void SendFCMToken(string token, string deviceType) {
		var request = new Dictionary<string, object>();
		request["Command"] = "SUI";
		request["Notifications"] = new Dictionary<string, object>();
		((Dictionary<string, object>)request["Notifications"])["RegistrationID"] = token;
		((Dictionary<string, object>)request["Notifications"])["DeviceType"] = deviceType;

		CommunicationManager.RequestAndGetResponse(request);
	}

	/**
	 * Used to send the full request to the CommunicationManager.  If the sole parameter for the request is the Command,
	 * the input request dictionary can be null.
	 * <param name="reqCommand">The command name: "LGN", "QGU", etc.</param>
	 * <param name="pc">The instance of the parent controller initiating the request</param>
	 * <param name="request">Dictionary describing the request, if default the request is created within the method</param>
	 */
	private static void BasicServerRequest(RequestType rt, ParentController pc, Dictionary<string, object> request = null){
		if(request == null){
			request = new Dictionary<string, object>();
		}
		request["Command"] = rt.ToString();

		string requestId = CommunicationManager.Request(request, pc);
		pc.SetRequestReadiness(requestId, ParentController.REQUEST_IS_NOT_READY);
		pc.RequestToType[requestId] = rt;
	}
}

public enum RequestType{
	CU  = 0,
	LGN = 1,
	GUI = 2,
	QGU = 3,
	IL  = 4
};
