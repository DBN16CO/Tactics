using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

/// This class holds the generic actions for any unit within the place units tab
public class PUUnit : UIAnimations, IPointerClickHandler {

	private int _id;
	private string _unitName;

#region // Public properties
	public int ID {
		get{return _id;}
	}
	public string UnitName {
		get{return _unitName;}
	}
#endregion

	// Sets unit info on generic unit within place units tab
	public static PUUnit Create(int id, string unitName, RectTransform transform) {
		// Set Unity data
		Object newObject = Instantiate(Resources.Load("Prefabs/PUUnit"), transform);
		PUUnit newUnit = (newObject as GameObject).GetComponent<PUUnit>();
		newUnit.gameObject.GetComponent<Image>().sprite =
			Resources.Load<Sprite>(GameData.GetUnit(unitName).SpritePath);
		newUnit.gameObject.name = unitName + "_" + id;

		// Set member variables
		newUnit._id = id;
		newUnit._unitName = unitName;

		return newUnit;
	}

	// Actions on click
	public void OnPointerClick(PointerEventData eventData) {
		// If selecting the already selected unit
		if(GameController.UnitBeingPlaced == this) {
			UnselectUnit(this);
			GameController.UnitBeingPlaced = null;
		}else {
			// If selecting new unit
			if(GameController.UnitBeingPlaced != null) {
				UnselectUnit(GameController.UnitBeingPlaced);
			}
			GameController.UnitBeingPlaced = this;
			SelectUnit(this);
		}
	}

	public void SelectUnit(PUUnit unit){
		unit.UIPop();
	}

	public void UnselectUnit(PUUnit unit){
		unit.UIUnpop();
	}

	// Unselected and removes placed unit
	public void RemoveUnit() {
		GameController.UnitBeingPlaced = null;
		UnselectUnit(this);
		GameController.PU.RemoveUnit(this);
	}

}
