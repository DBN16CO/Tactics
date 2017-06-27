using UnityEngine;					// Because we inherit from MonoBehaviour
using UnityEngine.EventSystems;

// Class governing the base object of gameplay
// Each grid square is a token and is the main form of player interaction
public class Token : MonoBehaviour {

	private int _x;					// X value of token
	private int _y;					// Y value of token
	private bool _canAttack;		// Can the selected unit attack this token
	private bool _canMove;			// Can the selected unit move to this token

	private TerrainData _terrain;	// The token's current terrain
	private Unit 	_unit;			// The unit currently on the token


#region Setters and Getters
	public TerrainData CurrentTerrain {
		get{return _terrain;}
		set{_terrain = value;}
	}
	public Unit CurrentUnit {
		get{return _unit;}
		set{_unit = value;}
	}
	public int X {
		get{return _x;}
		set{_x = value;}
	}
	public int Y {
		get{return _y;}
		set{_y = value;}
	}
	public bool CanAttack {
		get{return _canAttack;}
		set{_canAttack = value;}
	}
	public bool CanMove {
		get{return _canMove;}
		set{_canMove = value;}
	}

	// Booleans for place units
	public bool IsDisabled {
		get{return gameObject.GetComponent<SpriteRenderer>().material.name == "disabled (Instance)";}
	}
	private bool IsValidPlacement {
		get{return !IsDisabled && CurrentUnit == null && GameController.UnitBeingPlaced != null;}
	}
	private bool SelectingPlacedUnit {
		get{return CurrentUnit != null && GameController.UnitBeingPlaced == null;}
	}
#endregion


	// Called when token added to scene
	void Start() {
		CanMove = false;
		CanAttack = false;
	}

	// Called when the token is clicked - unselect if already selected
	// If CanMove, then you must already have a selected unit, so move
	void OnMouseDown() {
		if(!EventSystem.current.IsPointerOverGameObject()) { // This stops token action if other UI is over it
			if(GameController.PlacingUnits) {
				if(IsValidPlacement) {
					PlaceUnit();
				}else if(SelectingPlacedUnit) {
					SpawnController.ReturnPlacedUnit(CurrentUnit);
				}
			}else{ // Normal actions if not placing units
				if(CurrentUnit != null) {
					if(CanAttack) {

					}else {
						if(GameController.SelectedToken != null) {
							if(this != GameController.SelectedToken) {
								GameController.SelectedToken.CurrentUnit.UnselectUnit();
							}
						}
						CurrentUnit.Clicked(this);
					}
				}else if(CanMove) {
					if(GameController.IntendedMove != this) {
						SetIntendedMove();
					}else {
						ConfirmMove(GameController.SelectedToken);
					}
				}else {
					if(GameController.SelectedToken != null) {
						GameController.SelectedToken.CurrentUnit.UnselectUnit();
					}
				}
			}
		}
	}

	// Move unit from input prevToken to this token and unselect after
	private void SetIntendedMove() {
		GameController.IntendedMove = this;
		GameController.SelectedToken.CurrentUnit.transform.position = gameObject.transform.position;
	}
	// Move unit from input prevToken to this token and unselect after
	private void ConfirmMove(Token prevToken) {
		if(Server.TakeAction(prevToken.CurrentUnit.Info,"Wait", X, Y)) {
			CurrentUnit = prevToken.CurrentUnit;
			prevToken.CurrentUnit = null;
			CurrentUnit.UpdateInfo(X: X, Y: Y);
			CurrentUnit.TakenAction = true;
			CurrentUnit.PaintUnit("disable");
			GameController.SelectedToken = null;
			CurrentUnit.UnselectUnit();
		}
	}

	// Token actions when unit is placed
	private void PlaceUnit() {
		CurrentUnit = GameController.SC.CreateUnit(GameController.UnitBeingPlaced.matchUnit,X,Y, true);
	}

	// Sets properties based on action
	public void SetActionProperties(string action) {
		switch(action) {
			case "move":
				CanMove = true;
				break;
			case "attack":
				CanAttack = true;
				break;
			case "overwrite":
				CanMove = false;
				CanAttack = false;
				break;
			case "clear":
				CanMove = false;
				CanAttack = false;
				PaintAction(action);
				break;
			case "disabled":
				PaintAction(action);
				break;
		}
	}

	// Paints the token per the current action
	public void PaintAction(string action) {
		gameObject.GetComponent<SpriteRenderer>().material = Resources.Load<Material>("Materials/" + action);
	}

	// Sets the token's terrain based on string input
	public void SetTerrain(string shortName) {
		CurrentTerrain = GameData.GetTerrain(shortName);
		gameObject.name = CurrentTerrain.name;
		gameObject.GetComponent<SpriteRenderer>().sprite = Resources.Load<Sprite>(CurrentTerrain.spritePath);
	}

}
