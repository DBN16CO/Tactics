using UnityEngine;
using System;

// Class governing unit options
public class Unit : MonoBehaviour {

	private MatchUnit _info;
	private Stat[] _stats;
	// Situational stats
	private float _remainingMoveRange;

	private bool _selected;
	private bool _takenAction;
	private bool _myTeam;
	private GameController _gc;


#region Setters and Getters
	// Returns unit information
	public MatchUnit Info {
		get{return _info;}
		set{_info = value;}
	}
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
		name = name.Substring(0, name.Length-7);
		_gc = GameObject.Find("GameController").GetComponent<GameController>();
	}

	// Called from the clicked token - deselect if already selected
	public void Clicked(Token token) {
		if(_selected) {
			UnselectUnit();
		}else {
			_selected = true;
		// UI Options in GameController
			_gc.SelectUnit(token);
		}
	}

	// Public function to deselect this unit
	public void UnselectUnit() {
		_selected = false;
		_gc.UnselectUnit();
	}

	// Resets unit at start of turn
	public void Reset() {
		_takenAction = false;
		RemainingMoveRange = GameData.GetUnit(name).GetStat("Move").Value;
	}

}
