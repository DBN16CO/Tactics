using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenuController : MonoBehaviour {

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
		// Run the QGU command here. For now, just populate dummy games
		int numGames = 8;
		Transform activeGames = GameObject.Find("ActiveCustomGamesContent").transform;
		// For each game brought back, instantiate prefab and set position
		for(int i = 0; i < numGames; i++) {
			GameObject currGame = Instantiate(Resources.Load("Prefabs/ActiveCustomGame"), Vector3.zero, Quaternion.identity, activeGames) as GameObject;
			currGame.GetComponent<ActiveCustomGameController>().SetDetailedProperties(i);

			currGame.GetComponent<RectTransform>().anchoredPosition = new Vector3(0,-300 * i);
			currGame.transform.SetAsFirstSibling();
		}
		// Adjust the size of the scrollable area
		activeGames.GetComponent<RectTransform>().sizeDelta = new Vector3(Screen.width,300 * numGames);
	}

}
