using System;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class ActiveCustomGameController : MonoBehaviour {

	public Button btn;
	private GameObject _detailedView;

	private bool _expanding;			// When detailedview is expanding
	private bool _expanded;				// When detailedview is expanded
	public bool _collapsing;			// When detailedview is collapsing
	private float _t;					// Arbitrary measure of time
	private RectTransform _RT;			// Transform of this gameObject
	private RectTransform _parentRT;	// Transform of the parent scrollview
	private RectTransform _detailedViewRT; // Transform of the detailedview
	private float _maxY;
	private float _deltaY;				// The amount the detailedview lerped THIS frame
	private int _matchID;

	// Y position of bottom of detailed view, used to keep from lerping below screen
	public float DetailedGlobalY {
		get{return Mathf.Round(_RT.anchoredPosition.y - _RT.sizeDelta.y + _detailedViewRT.anchoredPosition.y);}
	}


	// Initialization - set variables & add click listener
	void Awake () {
		gameObject.name = gameObject.name.Substring(0, 16);
		_RT = gameObject.GetComponent<RectTransform>();
		_parentRT = transform.parent.GetComponent<RectTransform>();
		_maxY = transform.parent.parent.parent.gameObject.GetComponent<RectTransform>().sizeDelta.y;

		_expanding = false;
		_expanded = false;
		_collapsing = false;
		_t = 0f;

		btn.onClick.AddListener(SelectGame);
	}

	// Since can't pass params into Awake constructor, set detailed properties after instantiation
	public void SetDetailedProperties(MatchData matchData) {
		_matchID = matchData.MatchID;
 		btn.transform.Find("Text").GetComponent<Text>().text = matchData.Name;
 	}

	// Toggles whether to collapse or expand the detailedview
	void ToggleDetailedView() {
		_t = 0f;
		if(_expanding || _expanded) {
			_expanding = false;
			_collapsing = true;
		}else{
			_collapsing = false;
			_expanding = true;
		}
	}

	// Handles any button presses to the 
	void SelectGame() {
		GameData.CurrentMatch = GameData.GetMatches[_matchID];
		SceneManager.LoadSceneAsync("Game", LoadSceneMode.Single);
	}

	// Runs every frame - stop at t = 1 because lerp is from 0 to 1
	// Calculate deltaY to move all of the game prefabs under the one you click
	void Update () {
		if(_t >= 1f) {
			_expanded = _expanding;
			_expanding = false;
			_collapsing = false;
			_t = 0f;
		}else if(_expanding || _collapsing) {
			_t += Time.deltaTime;
			float preY = _detailedViewRT.anchoredPosition.y;
			_detailedViewRT.anchoredPosition = new Vector3(0,Mathf.Lerp(_detailedViewRT.anchoredPosition.y,Convert.ToInt32(_expanding) * -500,_t));
			_deltaY = _detailedViewRT.anchoredPosition.y - preY;
			LerpBelowGames();
			if(DetailedGlobalY < - _maxY - _parentRT.anchoredPosition.y) {
				_parentRT.anchoredPosition -= new Vector2(0,_deltaY);
			}else if(_parentRT.anchoredPosition.y + _maxY > _parentRT.sizeDelta.y) {
				_parentRT.anchoredPosition -= new Vector2(0,_deltaY);
			}
		}
	}

	// Moves all of the game prefabs under the one you clicked by using the sibling order
	// also resize parent transform (scrollable area)
	private void LerpBelowGames() {
		int currIndex = transform.GetSiblingIndex();
		for(int i = currIndex-1; i >= 0; i--) {
			RectTransform childRT = transform.parent.GetChild(i).GetComponent<RectTransform>();
			childRT.anchoredPosition = new Vector2(0,childRT.anchoredPosition.y + _deltaY);
		}
		_parentRT.sizeDelta -= new Vector2(0,_deltaY);
	}

}
