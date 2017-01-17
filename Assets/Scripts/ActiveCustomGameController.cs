using System;
using UnityEngine;
using UnityEngine.UI;

public class ActiveCustomGameController : MonoBehaviour {

	private MainMenuController _mc;

	public Button btn;
	private GameObject _detailedView;

	private bool _expanding;			// When detailedview is expanding
	private bool _expanded;				// When detailedview is expanded
	public bool _collapsing;			// When detailedview is collapsing
	private float _t;					// Arbitrary measure of time
	private RectTransform _detailedViewRT; // Transform of the detailedview
	private float _deltaY;				// The amount the detailedview lerped THIS frame

	// Initialization - set variables & add click listener
	void Awake () {
		_mc = GameObject.Find("MainMenuController").GetComponent<MainMenuController>();
		gameObject.name = gameObject.name.Substring(0, 16);

		_expanding = false;
		_expanded = false;
		_collapsing = false;
		_t = 0f;

		btn.onClick.AddListener(ToggleDetailedView);
		_detailedView = gameObject.transform.FindChild("DetailedView").gameObject;
	}

	// Since can't pass params into Awake constructor, set detailed properties after instantiation
	public void SetDetailedProperties(int index) {
		// Below code is for testing - makes the dummy games say Game1, Game2 etc
		_detailedView.name += (index + 1).ToString();
		btn.transform.FindChild("Text").GetComponent<Text>().text += (index + 1).ToString();

		_detailedViewRT = _detailedView.GetComponent<RectTransform>();
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
		}
	}

	// Moves all of the game prefabs under the one you clicked by using the sibling order
	// also resize parent transform (scrollable area)
	private void LerpBelowGames() {
		int currIndex = transform.GetSiblingIndex();
		int maxY = (transform.parent.childCount - 1) * -300;
		for(int i = currIndex-1; i >= 0; i--) {
			RectTransform childRT = transform.parent.GetChild(i).GetComponent<RectTransform>();
			childRT.anchoredPosition = new Vector2(0,childRT.anchoredPosition.y + _deltaY);
		}
		RectTransform parentRT = transform.parent.GetComponent<RectTransform>();
		parentRT.sizeDelta = new Vector2(1440,parentRT.sizeDelta.y - _deltaY);
	}

}
