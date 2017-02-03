using UnityEngine;
using System;
using UnityEngine.UI;

public class SelectUnitController : MonoBehaviour {

	private UnitData _data;
	private SetTeamController stc;

	public Sprite UnitImage {
		get{return gameObject.transform.FindChild("Image").GetComponent<Image>().sprite;}
		set{gameObject.transform.FindChild("Image").GetComponent<Image>().sprite = value;}
	}
	public string DisplayName {
		get{return gameObject.transform.FindChild("Name").GetComponent<Text>().text;}
		set{gameObject.transform.FindChild("Name").GetComponent<Text>().text = value;}
	}
	public int Price {
		get{return Int32.Parse(gameObject.transform.FindChild("Cost").GetComponent<Text>().text.Substring(1));}
		set{gameObject.transform.FindChild("Cost").GetComponent<Text>().text = "$" + value;}
	}
	public int Amount {
		get{return Int32.Parse(gameObject.transform.FindChild("NumBackground").transform.FindChild("Num").GetComponent<Text>().text.Substring(1));}
		set{gameObject.transform.FindChild("NumBackground").transform.FindChild("Num").GetComponent<Text>().text = "x" + value;}
	}


	public void AssignUnit(UnitData unitData) {
		stc = GameObject.Find("SetTeamController").GetComponent<SetTeamController>();
		_data = unitData;
		gameObject.name = _data.name;
		DisplayName = gameObject.name;
		UnitImage = Resources.Load<Sprite>(_data.spritePath);
		Price = _data.price;
		Amount = 0;
	}

	public void AddUnit() {
		if(stc.FundsRemaining >= Price) {
			Amount++;
			stc.FundsRemaining -= Price;
			stc.units.Add(DisplayName);
		}
	}

	public void RemoveUnit() {
		if(Amount > 0) {
			Amount--;
			stc.FundsRemaining += Price;
			stc.units.Remove(DisplayName);
		}
	}

	public void Test() {
		stc = GameObject.Find("SetTeamController").GetComponent<SetTeamController>();
		DisplayName = "Warrior";
		UnitImage = Resources.Load<Sprite>("Sprites/Units/axeman");
		Price = 100;
		Amount = 0;
	}

}
