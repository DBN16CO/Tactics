using UnityEngine;
using System;
using System.Collections.Generic;


public class GameController : MonoBehaviour {

	private Token[][] _tokens;
	private int _gridHeight;
	private int _gridLength;

	private List<Unit> _units;
	public static Token _selectedToken;
	private List<ValidAction> _actions;		// Array of valid moves


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
		// Testing
		Actions = new List<ValidAction>();
		Units = new List<Unit>();
		Test();
	}

	public void SelectUnit(Unit unit, Token token, bool takenAction) {
		SelectedToken = token;
		if(!takenAction) {
			SetValidActions(unit.name, token);
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

	private void SetValidActions(string unitName, Token token) {
		float range = 3f; // = Unit.GetRangeFromServer
		EvalSurroundingTokenActions(unitName, range, token);

		foreach(ValidAction action in Actions) {
			Tokens[action.col][action.row].SetActionProperties(action.action);
		}
	}

	private void EvalSurroundingTokenActions(string unitName, float range, Token token) {
		Token nextToken;
		// Start with above token
		if(token.Y < GridHeight) {
			nextToken = Tokens[token.X][token.Y+1];
			EvalNextToken(unitName, range, nextToken);
		}
		// Start with left token
		if(token.X > 0) {
			nextToken = Tokens[token.X-1][token.Y];
			EvalNextToken(unitName, range, nextToken);
		}
		// Start with below token
		if(token.Y > 0) {
			nextToken = Tokens[token.X][token.Y-1];
			EvalNextToken(unitName, range, nextToken);
		}
		// Start with right token
		if(token.X < GridLength) {
			nextToken = Tokens[token.X+1][token.Y];
			EvalNextToken(unitName, range, nextToken);
		}
	}

	private void EvalNextToken(string unitName, float range, Token token) {
		if(!token.CanMove && !token.CanAttack) {
			float remainingRange;
			remainingRange = EvalToken(unitName, range, token);
			if(remainingRange > 0f) {
				EvalSurroundingTokenActions(unitName, remainingRange, token);
			}
		}
	}

	private float EvalToken(string unitName, float range, Token token) {
		float remainingRange = range - TerrainMod.TerrainWeight(unitName, token.name);
		if(remainingRange >= 0f) {
			Actions.Add(AddValidAction("move", token.X, token.Y));
		}
		return (remainingRange >= 0f)? remainingRange : -1f;
	}

	private void ClearValidActions() {
		foreach(ValidAction action in Actions) {
			Tokens[action.col][action.row].SetActionProperties("clear");
		}
		Actions.Clear();
	}

	private ValidAction AddValidAction(string act, int col, int row) {
		ValidAction action;
		action.action = act;
		action.col = col;
		action.row = row;
		return action;
	}

#region Development
	// Runs at start of game
	private void Test() {
		// Create Grid and add test units
		SpawnController SC = gameObject.AddComponent<SpawnController>();
		Tokens = SC.CreateGrid(10);
		Units.Add(Tokens[2][3].CurrentUnit = SC.CreateUnit("Warrior",2,3));
		Units[0].MyTeam = true;

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
