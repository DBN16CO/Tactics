using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class MainMenuController : ParentController {

	private static int MOVE_BUTTON_DISTANCE;

	private Button _startRankedGame;

	private Button _cancelRankedButton;
	private Text _cancelRankedText;

	// Initiate variables and load active games
	void Start () {
		if(!Parse.Bool(Server.QueryGames()["Success"])) {
			Debug.Log("Query Games failed");
		}

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
			TimeSpan t = DateTime.UtcNow - new DateTime(1970, 1, 1);
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

					if(!Parse.Bool(Server.QueryGames(gameId)["Success"])) {
						Debug.Log("Query Games failed");
					}

					DisplayRankedGameButton();

					Transform activeGames = GameObject.Find("ActiveCustomGamesContent").transform;
					KeyValuePair<int, MatchData> pair = new KeyValuePair<int, MatchData>(gameId, GameData.Matches[gameId]);
					LoadCustomGame(activeGames, pair, GameData.Matches.Count - 1);

					// Adjust the size of the scrollable area
					activeGames.GetComponent<RectTransform>().sizeDelta = new Vector2(Screen.width,
						300 * (float)GameData.Matches.Count);
				}
			}
		}
	}

	public void LoadSetTeam() {
		SceneManager.LoadSceneAsync("SetTeam", LoadSceneMode.Single);
	}

	// Cancel the match search for the specific user
	public void CancelQueuedMatch(){
		if(!Parse.Bool(Server.CancelQueue())){
			//TODO
		}

		// Hide cancel button
		RectTransform rt = _cancelRankedButton.GetComponent<RectTransform>();
		rt.anchoredPosition = new Vector3(rt.anchoredPosition.x, rt.anchoredPosition.y + MOVE_BUTTON_DISTANCE);

		// Show set team button
		rt = _startRankedGame.GetComponent<RectTransform>();
		rt.anchoredPosition = new Vector3(rt.anchoredPosition.x, rt.anchoredPosition.y - MOVE_BUTTON_DISTANCE);
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

}
