using UnityEngine;
using System;
using UnityEngine.UI;

// This class controls each selectable Unit GameObject
public class SelectUnitController : ParentController {

	public UnitData data;
	private SetTeamController stc;

	// Controls the image of the selectable GameObject
	public Sprite UnitImage {
		get{return gameObject.transform.Find("Image").GetComponent<Image>().sprite;}
		set{gameObject.transform.Find("Image").GetComponent<Image>().sprite = value;}
	}
	// Controls the display name text of the selectable GameObject
	public string DisplayName {
		get{return gameObject.transform.Find("Name").GetComponent<Text>().text;}
		set{gameObject.transform.Find("Name").GetComponent<Text>().text = value;}
	}
	// Sets the price text of the selectable GameObject, returns the int
	public int Price {
		get{return Int32.Parse(gameObject.transform.Find("Cost").GetComponent<Text>().text.Substring(1));}
		set{gameObject.transform.Find("Cost").GetComponent<Text>().text = "$" + value;}
	}
	// Sets the amount text of the selectable GameObject, returns the int
	public int Amount {
		get{return Int32.Parse(gameObject.transform.Find("NumBackground").transform.Find("Num").GetComponent<Text>().text.Substring(1));}
		set{gameObject.transform.Find("NumBackground").transform.Find("Num").GetComponent<Text>().text = "x" + value;}
	}

	// Set specified game data on the selectable GameObject
	public void AssignUnit(UnitData unitData) {
		stc = GameObject.Find("SetTeamController").GetComponent<SetTeamController>();
		data = unitData;
		gameObject.name = data.Name;
		DisplayName = gameObject.name;
		UnitImage = Resources.Load<Sprite>(data.SpritePath);
		Price = data.Price;
		Amount = 0;
	}

	// Adds this unit to the unit list
	public void AddUnit() {
		SetTeamController.ErrorMessageText.text = "";

		if(stc.FundsRemaining >= Price) {
			Amount++;
			stc.FundsRemaining -= Price;
			stc.units.Add(DisplayName);
		}
	}
	// Removes this unit from the unit list
	public void RemoveUnit() {
		SetTeamController.ErrorMessageText.text = "";

		if(Amount > 0) {
			Amount--;
			stc.FundsRemaining += Price;
			stc.units.Remove(DisplayName);
		}
	}

}
