using UnityEngine;					// Because we inherit from MonoBehaviour

// Class governing the base object of gameplay
// Each grid square is a token and is the main form of player interaction
public class Token : MonoBehaviour {

	private int _x;					// X value of token
	private int _y;					// Y value of token

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
#endregion


	// Called when the token is clicked
	void OnMouseDown() {
		// If a unit is on the selected token
		if(CurrentUnit != null) {
			// Call unit's clicked function
			CurrentUnit.Clicked();
		}
		// Else if there is no unit
		else{
			Debug.Log(CurrentTerrain.Name + "(" + X + "," + Y + ")");
		}
	}

	// Sets the token's terrain based on string input
	// i.e. "Grass", "Forest", etc...
	public void SetTerrain(string terrain) {
		// Switch on input
		switch(terrain) {
			case "Grass":
				CurrentTerrain = new Grass(gameObject);
				break;
		}
	}

}
