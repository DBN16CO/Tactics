using UnityEngine;

// Class governing unit options
public class Unit : MonoBehaviour {

	private bool _selected;
	private bool _takenAction;
	private bool _myTeam;
	private GameController _gc;

#region Setters and Getters
	// Returns _myTeam;
	public bool MyTeam {
		get{return _myTeam;}
		set{_myTeam = value;}
	}
#endregion

	// Runs on unit instantiation
	void Start() {
		// Initialize vars
		_selected = false;
		_gc = GameObject.Find("Game Controller").GetComponent<GameController>();
	}

	// Called from the clicked token when there is a unit
	public void Clicked(Token token) {
		// If the unit is already selected, deselect
		if(_selected) {
			UnselectUnit();
		// Else select the unit
		}else {
			_selected = true;
		// UI Options if the unit is yours and has/hasn't taken its turn
			if(MyTeam) {
				_gc.SelectUnit(this, token, _takenAction);
		// UI Options if the unit isn't yours
			}else {
				_gc.ShowUnitInfo(this);
			}
		}
	}

	// Public function to deselect this unit
	public void UnselectUnit() {
		_selected = false;
		// Run associated game functions like re-painting grid
		_gc.UnselectUnit();
	}

}
