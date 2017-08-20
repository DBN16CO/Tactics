﻿using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

/// This class holds the generic actions for any unit within the place units tab
public class PUUnit : UIAnimations, IPointerClickHandler {

	private PlaceUnitsController _pu;
	public UnitInfo matchUnit;

	// Sets unit info on generic unit within place units tab
	public void SetInfo(UnitInfo unit) {
		_pu = GameObject.Find("PlaceUnits").GetComponent<PlaceUnitsController>();
		gameObject.GetComponent<Image>().sprite = Resources.Load<Sprite>(GameData.GetUnits[unit.Name].SpritePath);
		matchUnit = unit;
	}

	// Actions on click
	public void OnPointerClick(PointerEventData eventData) {
		// If selecting the already selected unit
		if(GameController.UnitBeingPlaced == this) {
			UnselectPU();
			GameController.UnitBeingPlaced = null;
		}else {
			// If selecting new unit
			if(GameController.UnitBeingPlaced != null) {
				GameController.UnitBeingPlaced.UnselectPU();
			}
			GameController.UnitBeingPlaced = this;
			SelectPU();
		}
	}

	// Unselected and removes placed unit
	public void RemoveUnit() {
		GameController.UnitBeingPlaced = null;
		UnselectPU();
		_pu.RemoveUnit(this);
	}

}
