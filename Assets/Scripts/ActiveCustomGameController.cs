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
	private RectTransform _detailedViewRT;
	private float _deltaY;

	// Use this for initialization
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

	public void SetDetailedProperties(int index) {
		_detailedView.name += (index + 1).ToString();
		btn.transform.FindChild("Text").GetComponent<Text>().text += (index + 1).ToString();

		_detailedViewRT = _detailedView.GetComponent<RectTransform>();
	}

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

	// Update is called once per frame
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
