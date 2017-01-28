using UnityEngine;
using System.Collections.Generic;

public class SwitchTabController : MonoBehaviour {

	private float numTabs;					// Number of tabs - float for math
	public List<GameObject> tabs;

	private int _selectedTabIndex;			// Index of whichever tab is selected
	private bool _moving;					// When you select a different tab
	private float _ttab;					// Arbitrary measure of time for tab movement
	private const float _ttabmax = 0.2f;	// Time it takes to move the selected tab
	private float _ttabmult;				// Multiplier calculated to make _ttabmax the time it takes
	private RectTransform _selectedTabRT;	// Transform of the moving tab
	private RectTransform _tabsContentRT;	// Transform of the tabs content parent

	// The real value of time to use for lerp functions
	private float _timetab {
		get{return _ttab * _ttabmult;}
	}

	// Use this for initialization
	void Start () {
		numTabs = tabs.Count;
		for(int i = 0; i < numTabs; i++) {
			if(tabs[i] != null) {
				tabs[i].GetComponent<RectTransform>().anchoredPosition = new Vector2(1440 * i,0);
			}
		}

		_selectedTabIndex = 0;
		_moving = false;
		_ttab = 0f;
		_ttabmult = 1f / _ttabmax;
		_selectedTabRT = (RectTransform)GameObject.Find("SelectedTab").transform;
		_tabsContentRT = (RectTransform)GameObject.Find("TabsContent").transform;
		_selectedTabRT.sizeDelta = new Vector2(1440f/numTabs,_selectedTabRT.sizeDelta.y);
	}

	// Runs every frame. Using GetKeyDown until mobile testing which will use swipe
	void Update () {
		if(Input.GetKeyDown("left") && _selectedTabIndex > 0){
			_selectedTabIndex--;
			SetMoveParams();
		}else if(Input.GetKeyDown("right") && _selectedTabIndex < numTabs-1){
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
				Mathf.Lerp(_selectedTabRT.anchoredPosition.x,_selectedTabIndex * (1440f/numTabs) ,_timetab),0);
			_tabsContentRT.anchoredPosition = new Vector2(Mathf.Lerp(_tabsContentRT.anchoredPosition.x,_selectedTabIndex * -1440,_timetab),-420);
		}
	}

	private void SetMoveParams() {
		_ttab = 0f;
		_moving = true;
	}

}
