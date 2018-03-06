using UnityEngine;
using System.Collections.Generic;

// Class governing unit options
public class Unit {
	private static readonly Vector3 U_UNIT_OFFSET = new Vector3(0, 0, -1);

	public static bool ALLY_TEAM  = true;
	public static bool ENEMY_TEAM = false;

	private string ALLY_HEX_COLOR     = "3A64FFFF";
	private string DISABLED_HEX_COLOR = "1D233CFF";
	private string ENEMY_HEX_COLOR    = "FF9C9CFF";

	private int 	_id;
	private string 	_unitName;
	private int 	_hp;
	private int     _maxHp;
	private int 	_x;
	private int 	_y;
	private bool 	_acted;

	private bool 	_myTeam;
	private bool 	_selected;

	private GameObject _unitObject;
	private Transform  _transform;
	private GameObject _maxHpBar;
	private GameObject _currHpBar;
	private const float U_DEF_HP_SCALE = 0.8f;

#region Setters and Getters
	public int ID {
		get{return _id;}
	}
	public string UnitName {
		get{return _unitName;}
	}
	public int HP {
		get{return _hp;}
	}
	public int X {
		get{return _x;}
	}
	public int Y {
		get{return _y;}
	}
	public bool Acted {
		get{return _acted;}
	}
	public bool MyTeam {
		get{return _myTeam;}
	}
	public bool Selected {
		get{return _selected;}
	}

	public Transform transform {
		get{return _transform;}
	}

#endregion

	// Constructor called when users places thier units during the PU phase
	public Unit(int id, string unitName, int x, int y) {
		_id 		= id;
		_unitName 	= unitName;
		_hp 		= GameData.GetUnit(_unitName).GetStat("HP").Value;
		_maxHp 		= GameData.GetUnit(_unitName).GetStat("HP").Value;
		_x 			= x;
		_y 			= y;
		_acted 		= false;

		_myTeam 	= true;
		_selected 	= false;

		_unitObject = null;
	}

	// Constructor called when initializing a map after the PU phase
	public Unit(Dictionary<string, object> unit, bool myTeam) {
		_id 		= Parse.Int(unit["ID"]);
		_unitName 	= Parse.String(unit["Name"]);
		_hp 		= Parse.Int(unit["HP"]);
		_maxHp 		= GameData.GetUnit(_unitName).GetStat("HP").Value;
		_x 			= Parse.Int(unit["X"]);
		_y 			= Parse.Int(unit["Y"]);
		_acted  	= Parse.Bool(unit["Acted"]);

		_myTeam		= myTeam;
		_selected 	= false;

		_unitObject = null;
	}

	public void Spawn(float scale) {
		_unitObject = GameObject.Instantiate(Resources.Load("Units/" + _unitName), Vector3.zero, Quaternion.identity,
			GameController.MapUnits.transform) as GameObject;

		// Move unit to location of its occupied token and move forward in z direction to move on top of movement arrows
		_unitObject.transform.position = GameController.Tokens[_x][_y].transform.position + U_UNIT_OFFSET;
		_unitObject.gameObject.transform.localScale = new Vector3(scale, scale, 1);
		_unitObject.gameObject.name = _unitName + "_" + _id;

		_transform = _unitObject.transform;
		_maxHpBar  = _transform.GetChild(0).gameObject;
		_currHpBar = _transform.GetChild(1).gameObject;
		if(!_myTeam){
			_currHpBar.GetComponent<SpriteRenderer>().color = Color.red;
		}
		ResizeHpBar();
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
			_unitObject.gameObject.transform.position = GameController.SelectedToken.gameObject.transform.position
				+ U_UNIT_OFFSET;
		}
		GameController.Main.UnselectUnit();
	}

	// Updates info, defaulting each parameter to itself
	// Pass in optional paramters via declaration: UpdateInfo(X: 5, Y: 7) to keep HP constant
	public void UpdateInfo(int newHP = -1, int newX = -1, int newY = -1) {
		_hp = (newHP == -1)? _hp : newHP;
		_x 	= (newX == -1)?  _x  : newX;
		_y 	= (newY == -1)?  _y  : newY;

		ResizeHpBar();
	}

	public void ConfirmMove(Token t) {
		_x = t.X;
		_y = t.Y;
		_acted = true;
		_selected = false;

		PaintUnit("disable");
		GameController.Main.UnselectUnit();
	}

	public void Destroy() {
		GameObject.Destroy(_unitObject.gameObject);
		_unitObject = null;
	}

	public void PaintUnit(string type) {
		switch(type) {
			case "ally":
				_unitObject.gameObject.GetComponent<SpriteRenderer>().color = GameController.HexToColor(ALLY_HEX_COLOR);
				break;
			case "disable":
				_unitObject.gameObject.GetComponent<SpriteRenderer>().color = GameController.HexToColor(DISABLED_HEX_COLOR);
				break;
			case "enemy":
				_unitObject.gameObject.GetComponent<SpriteRenderer>().color = GameController.HexToColor(ENEMY_HEX_COLOR);
				break;
		}
	}

	// Resets unit at start of turn
	public void Reset() {
		_acted = false;
		PaintUnit((_myTeam)? "ally": "enemy");
	}

	// Sets whether the unit has acted this turn yet
	public void SetActed(bool acted) {
		_acted = acted;
	}

	private void ResizeHpBar(){
		if(_hp == _maxHp){
			_maxHpBar.SetActive(false);
			_currHpBar.SetActive(false);
		}
		else{
			_maxHpBar.SetActive(true);
			_currHpBar.SetActive(true);
		}

		Vector3 scale = _currHpBar.transform.localScale;
		scale.x = (float)_hp / (float)_maxHp;
		_currHpBar.transform.localScale = scale;
	}

}
