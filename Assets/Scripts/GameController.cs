using UnityEngine;
//using System;
using System.Collections.Generic;


public class GameController : MonoBehaviour {

	// Server variables
	public int UserID;

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
		// Start the websocket connection
		Server.Connect();

		// Create user if necessary
		//Server.CreateUser("npriore", "tactics", "nr.priore@gmail.com");
		UserID = 1;


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
		AddValidAction("move", token);
		EvalSurroundingTokenActions(unit, token, range, "move");
		//EvalNextToken(unit, token, range, "move");

		foreach(ValidAction action in Actions) {
			Tokens[action.col][action.row].PaintAction(action.action);
		}
	}

	private void EvalSurroundingTokenActions(Unit unit, Token token, float range, string action) {
		Token nextToken;
		// Start with above token
		if(token.Y < GridHeight) {
			nextToken = Tokens[token.X][token.Y+1];
			EvalNextToken(unit, nextToken, token, range, action);
		}
		// Start with left token
		if(token.X > 0) {
			nextToken = Tokens[token.X-1][token.Y];
			EvalNextToken(unit, nextToken, token, range, action);
		}
		// Start with below token
		if(token.Y > 0) {
			nextToken = Tokens[token.X][token.Y-1];
			EvalNextToken(unit, nextToken, token, range, action);
		}
		// Start with right token
		if(token.X < GridLength) {
			nextToken = Tokens[token.X+1][token.Y];
			EvalNextToken(unit, nextToken, token, range, action);
		}
	}

	private void EvalNextToken(Unit unit, Token token, Token prevToken, float range, string action) {
		float remainingRange;
		remainingRange = EvalToken(unit.name, token, range, action);
		if(remainingRange >= 0f) {
			EvalSurroundingTokenActions(unit, token, remainingRange, action);
		}else if(action == "move") {
			if(action == "move" && prevToken.CurrentUnit != null) {
				EvalSurroundingTokenActions(unit, prevToken, unit.GetStat("AttackRange").Value-1, "attack");
			}else if(token.CurrentUnit != null) {
				if(!token.CurrentUnit.MyTeam) {
					EvalNextToken(unit, token, null, unit.GetStat("AttackRange").Value, "attack");
				}else{
					EvalSurroundingTokenActions(unit, token, unit.GetStat("AttackRange").Value-1, "attack");
				}
			}else{
				EvalNextToken(unit, token, null, unit.GetStat("AttackRange").Value, "attack");
			}
		}
	}

	private float EvalToken(string unitName, Token token, float range, string action) {
		if(token.CurrentUnit != null && action == "move") {
			if(!token.CurrentUnit.MyTeam) {
				return -1f;
			}
		}
		float remainingRange = (action == "move")? range - TerrainMod.TerrainWeight(unitName, token.name) : range - 1;
		if(remainingRange >= 0f) {
			if(token.CurrentUnit != null) {
				if(token.CurrentUnit.MyTeam) {
					return remainingRange;
				}
			}
			AddValidAction(action, token);
		}
		return remainingRange;
	}

	private void ClearValidActions() {
		foreach(ValidAction action in Actions) {
			Tokens[action.col][action.row].SetActionProperties("clear");
		}
		Actions.Clear();
	}

	private void AddValidAction(string act, Token token) {
		if(!token.CanMove && !token.CanAttack) {
			Actions.Add(CreateValidAction(act, token));
		}else if(act == "move" && token.CanAttack){
			RemoveValidAction(token);
			Actions.Add(CreateValidAction(act, token));
		}
	}

	private void RemoveValidAction(Token token) {
		for(int index = 0; index < Actions.Count; index++) {
			ValidAction currAction = Actions[index];
			if(currAction.col == token.X && currAction.row == token.Y) {
				Actions.Remove(currAction);
				token.SetActionProperties("overwrite");
			}
		}
	}

	private ValidAction CreateValidAction(string act, Token token) {
		ValidAction action;
		action.action = act;
		action.col = token.X;
		action.row = token.Y;
		token.SetActionProperties(act);
		return action;
	}

#region Development
	// Runs at start of game
	private void Test() {
		// Create Grid and add test units
		SpawnController SC = gameObject.AddComponent<SpawnController>();
		Tokens = SC.CreateGrid(12);
		Units.Add(Tokens[4][6].CurrentUnit = SC.CreateUnit("Warrior",4,6));
		Units.Add(Tokens[6][8].CurrentUnit = SC.CreateUnit("Warrior",6,8));
		Units.Add(Tokens[7][5].CurrentUnit = SC.CreateUnit("Warrior",7,5));
		Units.Add(Tokens[6][6].CurrentUnit = SC.CreateUnit("Warrior",6,6));
		Units[0].MyTeam = true;
		Units[1].MyTeam = true;
		Units[2].MyTeam = false;
		Units[3].MyTeam = false;

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
