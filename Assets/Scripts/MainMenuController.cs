using UnityEngine;

public class MainMenuController : MonoBehaviour {

	private int _selectedTabIndex;			// Index of whichever tab is selected
	private bool _moving;					// When you select a different tab
	private float _ttab;					// Arbitrary measure of time for tab movement
	private const float _ttabmax = 0.2f;	// Time it takes to move the selected tab
	private float _ttabmult;				// Multiplier calculated to make _ttabmax the time it takes
	private RectTransform _selectedTabRT;	// Transform of the moving tab

	// The real value of time to use for lerp functions
	private float _timetab {
		get{return _ttab * _ttabmult;}
	}

	// Initiate variables and load active games
	void Start () {
		_selectedTabIndex = 0;
		_moving = false;
		_ttab = 0f;
		_ttabmult = 1f / _ttabmax;
		_selectedTabRT = (RectTransform)GameObject.Find("SelectedTab").transform;

		LoadCustomGames();
	}

	// Loads active games - called custom because ranked will likely not have to be loaded
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
		activeGames.GetComponent<RectTransform>().sizeDelta = new Vector3(1440,300 * numGames);
	}

	// Runs every frame. Using GetKeyDown until mobile testing which will use swipe
	void Update () {
		if(Input.GetKeyDown("left") && _selectedTabIndex > 0){
			_selectedTabIndex--;
			SetMoveParams();
		}else if(Input.GetKeyDown("right") && _selectedTabIndex < 2){
			_selectedTabIndex++;
			SetMoveParams();
		}
		// Stop at time = 1 because Lerp function runs from 0 to 1
		if(_timetab >= 1) {
			_ttab = 0f;
			_moving = false;
		}else if(_moving) {
			_ttab += Time.deltaTime;
			_selectedTabRT.anchoredPosition = new Vector2(
				Mathf.Lerp(_selectedTabRT.anchoredPosition.x,_selectedTabIndex * 480,_timetab),
				-50);
		}
	}

	private void SetMoveParams() {
		_ttab = 0f;
		_moving = true;
	}

}
