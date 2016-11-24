using UnityEngine;
using System;

// Class governing unit options
public class Unit : MonoBehaviour {

	private Stat[] _stats;
	// Situational stats
	private float _remainingMoveRange;

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
	// Returns _stats
	public Stat[] Stats {
		get{return _stats;}
		set{_stats = value;}
	}
	// Returns specific stat
	public Stat GetStat(string statName) {
		return _stats[(int)Enum.Parse(typeof(UnitStats), statName)];
	}
	// Returns the remaining move range for this turn
	public float RemainingMoveRange {
		get{return _remainingMoveRange;}
		set{_remainingMoveRange = value;}
	}
	public bool TakenAction {
		get{return _takenAction;}
		set{_takenAction = value;}
	}
#endregion

	// Runs on unit instantiation
	public virtual void Awake() {
		// Initialize vars
		_selected = false;
		Stats = new Stat[Enum.GetValues(typeof(UnitStats)).Length];
		for(int cnt = 0; cnt < Stats.Length; cnt++) {
			Stats[cnt] = new Stat(Enum.GetName(typeof(UnitStats), cnt));
		}
		_gc = GameObject.Find("GameController").GetComponent<GameController>();
	}

	// Called from the clicked token when there is a unit
	public void Clicked(Token token) {
		// If the unit is already selected, deselect
		if(_selected) {
			UnselectUnit();
		// Else select the unit
		}else {
			_selected = true;
		// UI Options
			_gc.SelectUnit(this, token);
		}
	}

	// Public function to deselect this unit
	public void UnselectUnit() {
		_selected = false;
		// Run associated game functions like re-painting grid
		_gc.UnselectUnit();
	}

	// Resets unit at start of turn
	public void Reset() {
		_takenAction = false;
		RemainingMoveRange = GetStat("MoveRange").Value;
	}

}
