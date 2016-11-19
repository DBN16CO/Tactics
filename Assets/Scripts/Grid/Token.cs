using UnityEngine;					// Because we inherit from MonoBehaviour

// Class governing the base object of gameplay
// Each grid square is a token and is the main form of player interaction
public class Token : MonoBehaviour {

	private int _x;					// X value of token
	private int _y;					// Y value of token
	private bool _canAttack;		// Can the selected unit attack this token
	private bool _canMove;			// Can the selected unit move to this token

	private TokenTerrain _terrain;	// The token's current terrain
	private Unit 	_unit;			// The unit currently on the token


#region Setters and Getters
	// Returns _terrain
	public TokenTerrain CurrentTerrain {
		get{return _terrain;}
		set{_terrain = value;}
	}
	// Returns _unit
	public Unit CurrentUnit {
		get{return _unit;}
		set{_unit = value;}
	}
	// Returns the column of the token
	public int X {
		get{return _x;}
		set{_x = value;}
	}
	// Returns the row of the token
	public int Y {
		get{return _y;}
		set{_y = value;}
	}
	// Returns _canAttack
	public bool CanAttack {
		get{return _canAttack;}
		set{_canAttack = value;}
	}
	// Returns _canMove
	public bool CanMove {
		get{return _canMove;}
		set{_canMove = value;}
	}
#endregion


	// Called when token added to scene
	void Start() {
		// Initialize vars
		CanMove = false;
		CanAttack = false;
	}

	// Called when the token is clicked
	void OnMouseDown() {
		// If a unit is on the selected token
		if(CurrentUnit != null) {
			// Call unit's clicked function
			if(CurrentUnit.MyTeam && GameController.SelectedToken != null) {
				if(this != GameController.SelectedToken) {
					GameController.SelectedToken.CurrentUnit.UnselectUnit();
				}
			}
			CurrentUnit.Clicked(this);
		}
		// Else if there is no unit
		else{
			// If CanMove, then you must already have a selected unit, so move
			// Moves to this newly selected token, passing in the previously selected token
			if(CanMove) {
				MoveUnit(GameController.SelectedToken);
			}
		}
	}

	// Move unit from input prevToken to this token
	private void MoveUnit(Token prevToken) {
		Unit unit = prevToken.CurrentUnit;
		// Update current unit of 2 party tokens
		CurrentUnit = unit;
		prevToken.CurrentUnit = null;
		// Move unit's position
		unit.transform.position = gameObject.transform.position;
		// Unselect the unit
		unit.UnselectUnit();
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
		}
		// Paint token based on action
		//PaintAction(action);
	}

	// Paints the token per the current available action
	public void PaintAction(string action) {
		gameObject.GetComponent<SpriteRenderer>().material = Resources.Load("Materials/" + action) as Material;
	}

	// Sets the token's terrain based on string input
	// i.e. "Grass", "Forest", etc...
	public void SetTerrain(string terrain) {
		// Switch on input
		switch(terrain) {
			case "Grass":
				CurrentTerrain = new Grass(gameObject);
				break;
			case "Forest":
				CurrentTerrain = new Forest(gameObject);
				break;
		}
	}

}
