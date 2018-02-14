using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

/// This class controls the UI place units tab
public class PlaceUnitsController : ParentController {

	private List<PUUnit> _units;

	private RectTransform unitsRect;
	private GameObject _submit;

	// Runs when GameObject is added to scene
	void Start() {
		// Init game object vars
		name = name.Substring(0, name.Length-7);
		unitsRect = gameObject.GetComponent<ScrollRect>().content;

		// Init submit button vars
		_submit = gameObject.transform.Find("Submit").gameObject;
		_submit.GetComponent<Button>().onClick.AddListener(PlaceUnits);
		_submit.SetActive(false);

		// Init game vars
		_units = new List<PUUnit>();
		InitPlaceUnits();
	}

	// Runs when the app is closed - attempt to close the websocket cleanly
	void OnApplicationQuit() {
		CommunicationManager.OnDisable();
	}

	// Init the place units UI
	private void InitPlaceUnits() {
		foreach(Unit unit in GameData.CurrentMatch.AlliedUnits.Values) {
			AddUnit(unit);
		}
	}

	// Adds unit to place units tab and adjusts scroll rect
	public void AddUnit(Unit unit) {
		if(_submit.gameObject.activeSelf) {
			_submit.gameObject.SetActive(false);
		}

		// Instantiate the specified unit
		unitsRect.sizeDelta += new Vector2(70, 0);
		PUUnit _u = PUUnit.Create(unit.ID, unit.UnitName, unitsRect);
		_u.gameObject.GetComponent<RectTransform>().anchoredPosition3D = new Vector3(10 + 70 * _units.Count, 0, 0);

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
	void PlaceUnits(){
		Dictionary<string, object> response = Server.PlaceUnits(GameData.CurrentMatch);
		if(Parse.Bool(response["Success"])){
			GameController.PlacingUnits = false;
			for(int x = 0; x < GameController.Tokens.Length; x++) {
				for(int y = 0; y < GameController.Tokens[x].Length; y++) {
					GameController.Tokens[x][y].SetActionProperties("clear");
				}
			}
			Destroy(gameObject);
		}
		else{
			GameController.DisplayGameErrorMessage(Parse.String(response["Error"]));
		}
	}

}
