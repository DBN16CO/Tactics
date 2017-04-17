using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

/// This class controls the UI place units tab
public class PlaceUnitsController : MonoBehaviour {

	private GameController _gc;
	private List<PUUnit> _units;

	private RectTransform unitsRect;
	private GameObject _submit;

	// Runs when GameObject is added to scene
	void Start() {
		// Init game object vars
		name = name.Substring(0, name.Length-7);
		_gc = GameObject.Find("GameController").GetComponent<GameController>();
		unitsRect = gameObject.GetComponent<ScrollRect>().content;

		// Init submit button vars
		_submit = gameObject.transform.FindChild("Submit").gameObject;
		_submit.GetComponent<Button>().onClick.AddListener(PlaceUnits);
		_submit.SetActive(false);

		// Init game vars
		_units = new List<PUUnit>();
		InitPlaceUnits();
	}

	// Init the place units UI
	private void InitPlaceUnits() {
		for(int i = 0; i < _gc.myUnits.Count; i ++) {
			AddUnit(_gc.myUnits[i]);
		}
	}

	// Adds unit to place units tab and adjusts scroll rect
	public void AddUnit(MatchUnit unit) {
		if(_submit.gameObject.activeSelf) {
			_submit.gameObject.SetActive(false);
		}

		// Instantiate the specified unit
		unitsRect.sizeDelta += new Vector2(70, 0);
		PUUnit _u = (Instantiate(Resources.Load("Prefabs/PUUnit"),unitsRect) as GameObject).GetComponent<PUUnit>();
		_u.gameObject.GetComponent<RectTransform>().anchoredPosition3D = new Vector3(10 + 70 * _units.Count,0,0);
		_u.SetInfo(unit);

		_units.Add(_u);
	}

	// Removes unit from place units tab and adjusts scroll rect
	public void RemoveUnit(PUUnit unit) {
		for(int i = _units.IndexOf(unit) + 1; i < _units.Count; i++) {
			_units[i].gameObject.GetComponent<RectTransform>().anchoredPosition3D += new Vector3(-70,0,0);
		}
		unitsRect.sizeDelta -= new Vector2(70,0);
		_units.Remove(unit);
		Destroy(unit.gameObject);

		if(_units.Count == 0) {
			_submit.SetActive(true);
		}
	}

	// Action when submit button is pressed
	void PlaceUnits() {
		Debug.Log(Server.PlaceUnits(GameData.CurrentMatch));
		GameController.PlacingUnits = false;
		Destroy(gameObject);
	}

}
