using System.Collections.Generic;		// Dictionary

// Holds unit information mapped from database
public class UnitInfo {

	private int 	_id;
	private string 	_name;
	private int 	_hp;
	private int 	_x;
	private int 	_y;
	private bool 	_acted;

#region // Public properties
	public int ID {
		get{return _id;}
	}
	public string Name {
		get{return _name;}
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
#endregion


	// Default constructor
	public UnitInfo(Dictionary<string, object> unit) {
		_id 	= Parse.Int(unit["ID"]);
		_name 	= Parse.String(unit["Name"]);
		_hp 	= Parse.Int(unit["HP"]);
		_x 		= Parse.Int(unit["X"]);
		_y 		= Parse.Int(unit["Y"]);
		_acted  = Parse.Bool(unit["Acted"]);
	}

	// Updates info, defaulting each parameter to itself
	// Pass in optional paramters via declaration: UpdateInfo(X: 5, Y: 7) to keep HP constant
	public void UpdateInfo(int newHP = -1, int newX = -1, int newY = -1) {
		_hp = (newHP == -1)? _hp : newHP;
		_x 	= (newX == -1)?  _x  : newX;
		_y 	= (newY == -1)?  _y  : newY;
	}

	// Sets whether the unit has acted this turn yet
	public void SetActed(bool acted) {
		_acted = acted;
	}

}
