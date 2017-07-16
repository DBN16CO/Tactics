using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenuController : MonoBehaviour {

	// Initiate variables and load active games
	void Start () {
		Server.inQueue = false;
		LoadCustomGames();
	}

	// Runs when the app is closed - attempt to close the websocket cleanly
	void OnApplicationQuit() {
		CommunicationManager.OnDisable();
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
		int numGames = GameData.GetMatches.Count;
		for(int i = 0; i < numGames ; i++) {
			GameObject currGame = Instantiate(Resources.Load("Prefabs/ActiveCustomGame"), Vector3.zero, Quaternion.identity, activeGames) as GameObject;

			currGame.GetComponent<ActiveCustomGameController>().SetDetailedProperties(GameData.GetMatches[i]);
			currGame.GetComponent<RectTransform>().anchoredPosition3D = new Vector3(0,-300 * i);
			currGame.transform.SetAsFirstSibling();
		}
		// Adjust the size of the scrollable area
		activeGames.GetComponent<RectTransform>().sizeDelta = new Vector2(Screen.width,300 * numGames);
	}

}
