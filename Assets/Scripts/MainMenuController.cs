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
		if(!(bool)Server.QueryGames()["Success"]) {
			Debug.Log("Query Games failed");
		}

		MOVE_BUTTON_DISTANCE = Screen.height;
		_startRankedGame = GameObject.Find("RankedGameTab").transform.Find("Battle").gameObject.GetComponent<Button>();

		_cancelRankedButton = GameObject.Find("RankedGameTab").transform.Find("CancelBattle").gameObject.GetComponent<Button>();
		_cancelRankedText = _cancelRankedButton.transform.Find("Text").gameObject.GetComponent<Text>();

		// Determine which button to show for ranked games
		RectTransform rt = null;
		if(GameData.InGameQueue){
			rt = _startRankedGame.GetComponent<RectTransform>();
			rt.anchoredPosition = new Vector3(rt.anchoredPosition.x, rt.anchoredPosition.y + MOVE_BUTTON_DISTANCE);
		}
		else{
			rt = _cancelRankedButton.GetComponent<RectTransform>();
			rt.anchoredPosition = new Vector3(rt.anchoredPosition.x, rt.anchoredPosition.y + MOVE_BUTTON_DISTANCE);
		}

		LoadCustomGames();
	}

	void Update(){
		if(GameData.InGameQueue){
			TimeSpan t = DateTime.UtcNow - new DateTime(1970, 1, 1);
			int secondsSinceEpoch = (int)t.TotalSeconds;

			int deltaT = secondsSinceEpoch - GameData.FMStartTime;
			int deltaH = deltaT / 3600;
			int deltaM = (deltaT % 3600) / 60;
			int deltaS = (deltaT % 3600) % 60;
			_cancelRankedText.text = String.Format("Searching for match: {0:D}:{1:D2}:{2:D2}\nCancel.",
				deltaH, deltaM, deltaS);
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
	private void LoadCustomGames() {
		Transform activeGames = GameObject.Find("ActiveCustomGamesContent").transform;

		// For each game brought back, instantiate prefab and set position
		Dictionary<int, MatchData> _theMatches = GameData.Matches;
		int i = 0;
		foreach(KeyValuePair<int, MatchData> pair in _theMatches){
			GameObject currGame = Instantiate(Resources.Load("Prefabs/ActiveCustomGame"), Vector3.zero, Quaternion.identity, activeGames) as GameObject;

			currGame.GetComponent<ActiveCustomGameController>().SetDetailedProperties(pair);
			currGame.GetComponent<RectTransform>().anchoredPosition3D = new Vector3(0,-300 * i);
			currGame.transform.SetAsFirstSibling();

			i++;
		}
		// Adjust the size of the scrollable area
		activeGames.GetComponent<RectTransform>().sizeDelta = new Vector2(Screen.width, 300 * (float)_theMatches.Count);
	}

}
