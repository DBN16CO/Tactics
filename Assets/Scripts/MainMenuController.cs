using System;						// DateTime
using System.Collections.Generic;	// Dictionary
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class MainMenuController : ParentController {

	private static readonly DateTime MMC_EPOCH = new DateTime(1970, 1, 1);

	private static int MOVE_BUTTON_DISTANCE;

	private Button _startRankedGame;

	private Button _cancelRankedButton;
	private Text _cancelRankedText;

	void Awake(){
		// Populate dictionary of called sever functions
		_functionMapping[RequestType.QGU] = HandleQguResponse;
		_functionMapping[RequestType.CS]  = HandleCsResponse;
		_functionMapping[RequestType.SUI] = HandleSuiResponse;
	}

	// Initiate variables and load active games
	void Start () {
		Firebase.Messaging.FirebaseMessaging.TokenReceived += OnTokenReceived;
	//	Firebase.Messaging.FirebaseMessaging.MessageReceived += OnMessageReceived;

		MOVE_BUTTON_DISTANCE = Screen.height;
		_startRankedGame = GameObject.Find("RankedGameTab").transform.Find("Battle").gameObject.GetComponent<Button>();

		_cancelRankedButton = GameObject.Find("RankedGameTab").transform.Find("CancelBattle").gameObject.GetComponent<Button>();
		_cancelRankedText = _cancelRankedButton.transform.Find("Text").gameObject.GetComponent<Text>();

		DisplayRankedGameButton();

		LoadAllCustomGames();
	}

	void Update(){
		if(GameData.InGameQueue){
			// Update time the user has been waiting for a match
			TimeSpan t = DateTime.UtcNow - MMC_EPOCH;
			int secondsSinceEpoch = (int)t.TotalSeconds;

			int deltaT = secondsSinceEpoch - GameData.FMStartTime;
			int deltaH = deltaT / 3600;
			int deltaM = (deltaT % 3600) / 60;
			int deltaS = (deltaT % 3600) % 60;
			_cancelRankedText.text = String.Format("Searching for match: {0:D}:{1:D2}:{2:D2}\nCancel.",
				deltaH, deltaM, deltaS);

			// If in queue, check for async message about a found match
			Queue<Dictionary<string, object>> asyncMessages = CommunicationManager.GetAsyncKeyQueue("MATCH_FOUND");

			// If an opponent has been found
			if(asyncMessages != null && asyncMessages.Count > 0){
				Dictionary<string, object> currentMessage = asyncMessages.Dequeue();
				Dictionary<string, object> data = (Dictionary<string, object>)currentMessage["Data"];

				// A game ID and unit must be provided
				if(data.ContainsKey("Game_ID")){
					int gameId = Parse.Int(data["Game_ID"]);

					Server.QueryGames(this, gameId);
				}
			}
		}

		ProcessResponses();
	}

	public void OnTokenReceived(object sender, Firebase.Messaging.TokenReceivedEventArgs token) {
		Debug.Log("Received Registration Token: " + token.Token);

		Server.SendFCMToken(this, token.Token, "android");
	}

	public void OnMessageReceived(object sender, Firebase.Messaging.MessageReceivedEventArgs e) {
		Debug.Log("Received a new message from: " + e.Message.From);
	}

	public void LoadSetTeam() {
		SceneManager.LoadSceneAsync("SetTeam", LoadSceneMode.Single);
	}

	// Cancel the match search for the specific user
	public void CancelQueuedMatch(){
		LoadingCircle.Show();
		Server.CancelQueue(this);
	}

	// Loads active games
	private void LoadAllCustomGames() {
		Transform activeGames = GameObject.Find("ActiveCustomGamesContent").transform;

		// For each game brought back, instantiate prefab and set position
		Dictionary<int, MatchData> _theMatches = GameData.Matches;
		int i = 0;
		foreach(KeyValuePair<int, MatchData> pair in _theMatches){
			LoadCustomGame(activeGames, pair, i);

			i++;
		}
		// Adjust the size of the scrollable area
		activeGames.GetComponent<RectTransform>().sizeDelta = new Vector2(Screen.width, 300 * (float)_theMatches.Count);
	}

	// Load a single game (like when a match is found)
	private void LoadCustomGame(Transform activeGames, KeyValuePair<int, MatchData> pair, int idx){
		GameObject currGame = Instantiate(Resources.Load("Prefabs/ActiveCustomGame"), Vector3.zero, Quaternion.identity, activeGames) as GameObject;

		currGame.GetComponent<ActiveCustomGameController>().SetDetailedProperties(pair);
		currGame.GetComponent<RectTransform>().anchoredPosition3D = new Vector3(0,-300 * idx);
		currGame.transform.SetAsFirstSibling();
	}

	// Determine which button to show for ranked games
	private void DisplayRankedGameButton(){
		RectTransform rt = null;
		if(GameData.InGameQueue){
			// Move cancel button into view
			rt = _cancelRankedButton.GetComponent<RectTransform>();
			rt.anchoredPosition = new Vector3(rt.anchoredPosition.x, 0);

			// Hide start ranked game button
			rt = _startRankedGame.GetComponent<RectTransform>();
			rt.anchoredPosition = new Vector3(rt.anchoredPosition.x, rt.anchoredPosition.y + MOVE_BUTTON_DISTANCE);
		}
		else{
			// Move start ranked game button into view
			rt = _startRankedGame.GetComponent<RectTransform>();
			rt.anchoredPosition = new Vector3(rt.anchoredPosition.x, 0);

			// Hide cancel button
			rt = _cancelRankedButton.GetComponent<RectTransform>();
			rt.anchoredPosition = new Vector3(rt.anchoredPosition.x, rt.anchoredPosition.y + MOVE_BUTTON_DISTANCE);
		}
	}

	// Handles when a match is found and the new game needs to be added to the user's list
	private void HandleQguResponse(Dictionary<string, object> response){
		GameData.SetMatchData(response);
		GameData.SetMatchQueueData(response);

		if(response["Games"].ToString() == "[]"){
			Debug.Log("ERROR: QGU did not return any games.");

			return;
		}

		DisplayRankedGameButton();

		Transform activeGames = GameObject.Find("ActiveCustomGamesContent").transform;

		List<object> matches = Json.ToList(Parse.String(response["Games"]));
		Dictionary<string, object> matchDataAsDict;
		int gameId;

		// Populate the list of games with the new game(s)
		foreach(object match in matches) {
			matchDataAsDict = Json.ToDict(Parse.String(match));
			gameId = Parse.Int(matchDataAsDict["ID"]);

			KeyValuePair<int, MatchData> pair = new KeyValuePair<int, MatchData>(gameId, GameData.Matches[gameId]);
			LoadCustomGame(activeGames, pair, GameData.Matches.Count - 1);
		}

		// Adjust the size of the scrollable area
		activeGames.GetComponent<RectTransform>().sizeDelta = new Vector2(Screen.width,
			300 * (float)GameData.Matches.Count);
	}

	// Handles when the player wants to cancel searching for a match
	private void HandleCsResponse(Dictionary<string, object> response){
		LoadingCircle.Hide();

		// Hide cancel button
		RectTransform rt = _cancelRankedButton.GetComponent<RectTransform>();
		rt.anchoredPosition = new Vector3(rt.anchoredPosition.x, rt.anchoredPosition.y + MOVE_BUTTON_DISTANCE);

		// Show set team button
		rt = _startRankedGame.GetComponent<RectTransform>();
		rt.anchoredPosition = new Vector3(rt.anchoredPosition.x, rt.anchoredPosition.y - MOVE_BUTTON_DISTANCE);
	}

	private void HandleSuiResponse(Dictionary<string, object> response){
		// Do nothing?!
	}

}
