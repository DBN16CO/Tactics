using UnityEngine;
using System;
using System.Collections.Generic;


public class GameController : MonoBehaviour {

	private Token[][] _tokens;
	private int _gridHeight;
	private int _gridLength;

	private List<Unit> _units;
	private static Token _selectedToken;
	private List<ValidAction> _actions;		// Array of valid moves

	// Game Settings
	public static string GridAlpha;


#region Setters and Getters
	// Returns _tokens
	public Token[][] Tokens {
		get{return _tokens;}
		set{_tokens = value;}
	}
	// Returns _gridHeight
	public int GridHeight {
		get{return _gridHeight;}
		set{_gridHeight = value;}
	}
	// Returns _gridLength
	public int GridLength {
		get{return _gridLength;}
		set{_gridLength = value;}
	}
	// Returns _units
	public List<Unit> Units {
		get{return _units;}
		set{_units = value;}
	}
	// Returns _selectedToken
	public static Token SelectedToken {
		get{return _selectedToken;}
		set{_selectedToken = value;}
	}
	// Returns valid moves array
	public List<ValidAction> Actions {
		get{return _actions;}
		set{_actions = value;}
	}
#endregion


	void Start() {
		// Initialize vars
		Actions = new List<ValidAction>();
		Units = new List<Unit>();

		// Set game vars
		GridAlpha = "33";

		// Testing
		Test();
		StartTurn();
	}

	public void StartTurn() {
		foreach(Unit unit in Units) {
			if(unit.MyTeam) {
				unit.Reset();
			}
		}
	}

	public void SelectUnit(Unit unit, Token token, bool takenAction) {
		SelectedToken = token;
		if(!takenAction) {
			SetValidActions(unit, token);
		}else{
			ShowUnitInfo(unit);
		}
	}

	public void ShowUnitInfo(Unit unit) {

	}

	public void UnselectUnit() {
		SelectedToken = null;
		ClearValidActions();
	}

	private void SetValidActions(Unit unit, Token token) {
		float range = unit.RemainingMoveRange;
		Actions.Add(AddValidAction("move", token));
		EvalSurroundingTokenActions(unit, token, range, "move");
		//EvalNextToken(unit, token, range, "move");

		foreach(ValidAction action in Actions) {
			Tokens[action.col][action.row].SetActionProperties(action.action);
		}
	}

	private void EvalSurroundingTokenActions(Unit unit, Token token, float range, string action) {
		Token nextToken;
		// Start with above token
		if(token.Y < GridHeight) {
			nextToken = Tokens[token.X][token.Y+1];
			EvalNextToken(unit, nextToken, range, action);
		}
		// Start with left token
		if(token.X > 0) {
			nextToken = Tokens[token.X-1][token.Y];
			EvalNextToken(unit, nextToken, range, action);
		}
		// Start with below token
		if(token.Y > 0) {
			nextToken = Tokens[token.X][token.Y-1];
			EvalNextToken(unit, nextToken, range, action);
		}
		// Start with right token
		if(token.X < GridLength) {
			nextToken = Tokens[token.X+1][token.Y];
			EvalNextToken(unit, nextToken, range, action);
		}
	}

	private void EvalNextToken(Unit unit, Token token, float range, string action) {
		if(!token.CanMove && !token.CanAttack) {
			float remainingRange;
			remainingRange = EvalToken(unit.name, token, range, action);
			if(remainingRange > 0f) {
				EvalSurroundingTokenActions(unit, token, remainingRange, "move");
			}else if(action == "move") {
				EvalSurroundingTokenActions(unit, token, unit.GetStat("AttackRange").Value, "attack");
			}
		}
	}

	private float EvalToken(string unitName, Token token, float range, string action) {
		if(token.CurrentUnit != null) {
			if(!token.CurrentUnit.MyTeam) {
				return -1f;
			}
		}
		float remainingRange = (token == SelectedToken)? range : (action == "move")? range - TerrainMod.TerrainWeight(unitName, token.name) : range - 1f;
		if(remainingRange >= 0f) {
			Actions.Add(AddValidAction(action, token));
		}
		return remainingRange;
	}

	private void ClearValidActions() {
		foreach(ValidAction action in Actions) {
			Tokens[action.col][action.row].SetActionProperties("clear");
		}
		Actions.Clear();
	}

	private ValidAction AddValidAction(string act, Token token) {
		ValidAction action;
		action.action = act;
		action.col = token.X;
		action.row = token.Y;
		return action;
	}

#region Development
	// Runs at start of game
	private void Test() {
		// Create Grid and add test units
		SpawnController SC = gameObject.AddComponent<SpawnController>();
		Tokens = SC.CreateGrid(12);
		Units.Add(Tokens[4][4].CurrentUnit = SC.CreateUnit("Warrior",4,4));
		Units.Add(Tokens[6][6].CurrentUnit = SC.CreateUnit("Warrior",6,6));
		Units[0].MyTeam = true;
		Units[1].MyTeam = true;

		// Create terrain weight map
		TerrainMod.CreateWeightMap();
	}

	// Runs every frame
	void Update() {
		// Testing move/zoom
		if(Input.GetKey("up")){
			Camera.main.transform.position += Vector3.up * 0.1f;
		}
		if(Input.GetKey("down")){
			Camera.main.transform.position += Vector3.down * 0.1f;
		}
		if(Input.GetKey("left")){
			Camera.main.transform.position += Vector3.left * 0.1f;
		}
		if(Input.GetKey("right")){
			Camera.main.transform.position += Vector3.right * 0.1f;
		}
		if(Input.GetKey("i")){
			Camera.main.orthographicSize *= (Camera.main.orthographicSize < 0.5f)? 1f : 0.95f;
		}
		if(Input.GetKey("o")){
			Camera.main.orthographicSize /= 0.95f;
		}
	}
#endregion

}

public struct ValidAction {
	public string action;
	public int col;
	public int row;
}
