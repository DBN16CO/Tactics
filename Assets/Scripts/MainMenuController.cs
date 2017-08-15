using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenuController : ParentController {

	// Initiate variables and load active games
	void Start () {
		Server.inQueue = false;
		LoadCustomGames();
	}

	public void LoadSetTeam() {
		SceneManager.LoadSceneAsync("SetTeam", LoadSceneMode.Single);
	}

	// Loads active games
	private void LoadCustomGames() {
		if(!(bool)Server.QueryGames()["Success"]) {
			Debug.Log("Query Games failed");
		}
		Transform activeGames = GameObject.Find("ActiveCustomGamesContent").transform;

		// For each game brought back, instantiate prefab and set position
		Dictionary<int, MatchData> _theMatches = GameData.GetMatches;
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
