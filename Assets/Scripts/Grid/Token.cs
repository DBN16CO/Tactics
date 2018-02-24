using UnityEngine;					// Because we inherit from MonoBehaviour
using UnityEngine.EventSystems;

// Class governing the base object of gameplay
// Each grid square is a token and is the main form of player interaction
public class Token : MonoBehaviour {

	private int _x;					// X value of token
	private int _y;					// Y value of token

	private bool _canAttack;		// Can the selected unit attack this token
	private bool _canHeal;			// Can the selected unit heal this token
	private bool _canMove;			// Can the selected unit move to this token

	private TerrainData _terrain;	// The token's current terrain
	private Unit 	_unit;			// The unit currently on the token


#region Setters and Getters
	public TerrainData CurrentTerrain {
		get{return _terrain;}
	}
	public Unit CurrentUnit {
		get{return _unit;}
		set{_unit = value;}
	}
	public int X {
		get{return _x;}
	}
	public int Y {
		get{return _y;}
	}
	public bool CanAttack {
		get{return _canAttack;}
	}
	public bool CanHeal {
		get{return _canHeal;}
	}
	public bool CanMove {
		get{return _canMove;}
	}
#endregion

	public static Token Create(int x, int y, string terrainType, float scale, float size){
		// Instantiate token at each grid position
		Vector3 position = new Vector2(((float)x * scale) - size, -((float)y * scale) + size) +
			new Vector2(scale / 2f, - scale / 2f);
		Object tokenObj = Instantiate(Resources.Load("Prefabs/Token"), position, Quaternion.identity,
			GameController.MapTokens.transform);
		Token token = (tokenObj as GameObject).GetComponent<Token>();

		// Coordinates
		token._x = x;
		token._y = y;

		// Terrain Type
		token._terrain = GameData.GetTerrain(terrainType);
		token.gameObject.name = token._terrain.Name + " (" + token._x + ", " + token._y + ")";
		token.gameObject.GetComponent<SpriteRenderer>().sprite = Resources.Load<Sprite>(token._terrain.SpritePath);

		// Token Targeting Properties
		token._canAttack = false;
		token._canHeal = false;
		token._canMove = false;

		// Unit
		token._unit = null;

		// Scale
		token.gameObject.transform.localScale = new Vector3(scale, scale, 1);

		return token;
	}

	// Booleans for place units
	public bool IsDisabled() {
		return gameObject.GetComponent<SpriteRenderer>().material.name == "disabled (Instance)";
	}
	public bool HasEnemy() {
		if(_unit == null){
			return false;
		}
		return (!_unit.MyTeam)? true : false;
	}
	public bool HasAlly() {
		if(_unit == null){
			return false;
		}
		return (_unit.MyTeam)? true : false;
	}

	// Called when the token is clicked - unselect if already selected
	// If CanMove, then you must already have a selected unit, so move
	void OnMouseDown() {
		// Stops token action if other UI is over it
		if(EventSystem.current.IsPointerOverGameObject()) {
			return;
		}

		GameObject.Find("GameController").GetComponent<GameController>().HandleTokenClick(this);
	}

	// Sets properties based on action
	public void SetActionProperties(string action) {
		_canAttack = false;
		_canHeal = false;
		_canMove = false;

		switch(action) {
			case "attack":
				_canAttack = true;
				break;
			case "heal":
				_canHeal = true;
				break;
			case "move":
				_canMove = true;
				break;
			case "clear":
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

}
