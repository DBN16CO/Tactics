using UnityEngine;
using System.Collections.Generic;

// Class governing unit options
public class Unit : MonoBehaviour {

	private MatchUnit _info;
	private Dictionary<string, Stat> _stats;
	// Situational stats
	private int  _remainingMoveRange;

	private bool _selected;
	private bool _takenAction;
	private bool _myTeam;


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
	public bool TakenAction {
		get{return _takenAction;}
		set{_takenAction = value;}
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

	// Updates matchunit info, defaulting each parameter to itself
	// Pass in optional paramters via declaration: UpdateInfo(X: 5, Y: 7) to keep HP constant
	public void UpdateInfo(int HP = -1, int X = -1, int Y = -1) {
		MatchUnit tempUnit = Info;
		tempUnit.HP = (HP == -1)? tempUnit.HP : HP;
		tempUnit.X = (X == -1)? tempUnit.X : X;
		tempUnit.Y = (Y == -1)? tempUnit.Y : Y;
		Info = tempUnit;
		UpdateInfoStruct();		
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
		UpdateInfo(X: GameController.IntendedMove.X, Y: GameController.IntendedMove.Y);
		TakenAction = true;
		_info.Acted = true;
		UpdateInfoStruct();
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
		TakenAction = false;
		_info.Acted = false;
		PaintUnit((MyTeam)?"ally":"enemy");
		UpdateInfoStruct();

	}

	// Updates the 'Info' struct everywhere it has been duplicated, currently:
	// AlliedUnits or EnemyUnits
	public void UpdateInfoStruct(){
		if(MyTeam){
			GameData.CurrentMatch.AlliedUnits[Info.ID] = Info;
		}
		else{
			GameData.CurrentMatch.EnemyUnits[Info.ID] = Info;
		}
	}

}
