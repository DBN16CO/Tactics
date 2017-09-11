using UnityEngine;
using System.Collections.Generic;

// Class governing unit options
public class Unit : MonoBehaviour {

	private UnitInfo _info;
	private Dictionary<string, Stat> _stats;
	// Situational stats
	private int  _remainingMoveRange;

	private bool _selected;
	private bool _myTeam;


#region Setters and Getters
	// Returns unit information
	public UnitInfo Info {
		get{return _info;}
		set{_info = value;}
	}
	// Returns _myTeam;
	public bool MyTeam {
		get{return _myTeam;}
		set{_myTeam = value;}
	}
	// Returns _stats
	public Dictionary<string, Stat> Stats {
		get{return _stats;}
		set{_stats = value;}
	}
	// Returns specific stat
	public Stat GetStat(string statName) {
		return _stats[statName];
	}
	// Returns the remaining move range for this turn
	public int RemainingMoveRange {
		get{return _remainingMoveRange;}
		set{_remainingMoveRange = value;}
	}
#endregion

	// Runs on unit instantiation
	public virtual void Awake() {
		// Initialize vars
		_selected = false;
		Stats = new Dictionary<string, Stat>();
		name = name.Substring(0, name.Length-7);
	}

	// Called from the clicked token - deselect if already selected
	public void Clicked(Token token) {
		if(_selected) {
			UnselectUnit();
		}else {
			_selected = true;
		// UI Options in GameController
			GameController.Main.SelectUnit(token);
		}
	}

	// Public function to deselect this unit
	public void UnselectUnit() {
		_selected = false;
		if(GameController.SelectedToken != null) {
			gameObject.transform.position = GameController.SelectedToken.gameObject.transform.position;
		}
		GameController.Main.UnselectUnit();
	}

	public void ConfirmMove() {
		_selected = false;
		_info.UpdateInfo(newX: GameController.IntendedMove.X, newY: GameController.IntendedMove.Y);
		_info.SetActed(true);
		PaintUnit("disable");
		GameController.Main.UnselectUnit();
	}

	public void DestroyUnit() {
		Destroy(gameObject);
	}

	public void PaintUnit(string type) {
		switch(type) {
			case "enemy":
				gameObject.GetComponent<SpriteRenderer>().color = GameController.HexToColor("FF9C9CFF");
				break;
			case "ally":
				gameObject.GetComponent<SpriteRenderer>().color = GameController.HexToColor("3A64FFFF");
				break;
			case "disable":
				gameObject.GetComponent<SpriteRenderer>().color = GameController.HexToColor("1D233CFF");
				break;
		}
	}

	// Resets unit at start of turn
	public void Reset() {
		_info.SetActed(false);
		PaintUnit((_myTeam)?"ally":"enemy");
	}

}
