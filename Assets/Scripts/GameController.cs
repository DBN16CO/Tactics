using UnityEngine;
//using System;
//using System.Collections;
using System.Collections.Generic;


public class GameController : MonoBehaviour {

	private Token[][] _tokens;
	private int _gridHeight;
	private int _gridLength;

	private List<Unit> _units;
	private static Token _selectedToken;
	private List<ValidAction> _actions;		// Array of valid moves

	// Game Settings


#region Setters and Getters
	public Token[][] Tokens {
		get{return _tokens;}
		set{_tokens = value;}
	}
	public int GridHeight {
		get{return _gridHeight;}
		set{_gridHeight = value;}
	}
	public int GridLength {
		get{return _gridLength;}
		set{_gridLength = value;}
	}
	public List<Unit> Units {
		get{return _units;}
		set{_units = value;}
	}
	public static Token SelectedToken {
		get{return _selectedToken;}
		set{_selectedToken = value;}
	}
	public List<ValidAction> Actions {
		get{return _actions;}
		set{_actions = value;}
	}
#endregion


	// Ultimately, this will run on match generation
	// Development - place anything we need to initialize for dev/test here
	void Start() {
		// Not testing - will likely actually apply for match generation
		// Initialize match variables
		Actions = new List<ValidAction>();
		Units = new List<Unit>();

		// Block for testing -------------------------------------------
		// Set startup variables
		TestStartup();
		// Prereq server variables and functions
		TestServer();
		// For any gameplay vars and functions
		TestGamePlay();
		// End testing block -------------------------------------------

		// Not testing - will likely actually apply for match generation
		// Initialize turn
		StartTurn();
	}

	// Run when turn starts to reset units, etc
	public void StartTurn() {
		foreach(Unit unit in Units) {
			if(unit.MyTeam) {
				unit.Reset();
			}
		}
	}

	// Runs when a unit is selected. Take action if possible, otherwise show unit info
	public void SelectUnit(Unit unit, Token token) {
		SelectedToken = token;
		if(unit.MyTeam && !unit.TakenAction) {
			SetValidActions(unit, token);
		}else{
			ShowUnitInfo(unit);
		}
	}

	// Placeholder for what will contain code to show unit's info on UI
	public void ShowUnitInfo(Unit unit) {

	}

	// Runs when a unit is unselected (i.e. user clicks other unit, or unit takes turn)
	public void UnselectUnit() {
		SelectedToken = null;
		ClearValidActions();
	}

	// Begins the process to asses valid moves for the selected unit
	// Set range to unit's remaining range (in case we make units able to move twice if it has leftover)
	// After all actions have been assessed, paint the tokens
	private void SetValidActions(Unit unit, Token token) {
		float range = unit.RemainingMoveRange;
		AddValidAction("move", token);
		EvalSurroundingTokenActions(unit, token, range, "move");

		foreach(ValidAction action in Actions) {
			Tokens[action.col][action.row].PaintAction(action.action);
		}
	}

	// Evaluates the surrounding tokens for valid actions
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

	// Evaluates the specified token and determines to either continue movement, switch to attack, or end
	// If there is range remaining, evaluate surrounding tokens with whatever the current action is (move or attack)
	// If there is no range remaining, switch to attack action or end
	private void EvalNextToken(Unit unit, Token token, Token prevToken, float range, string action) {
		float remainingRange;
		remainingRange = EvalToken(unit.name, token, range, action);
		if(remainingRange >= 0f) {
			EvalSurroundingTokenActions(unit, token, remainingRange, action);
		}else if(action == "move") {
			if(prevToken.CurrentUnit != null) {
				// We can't move to this token or the previous token
				// Evaluate the prevToken with atkrange-1 since we're really trying to eval prevprevtoken
				EvalSurroundingTokenActions(unit, prevToken, unit.GetStat("AttackRange").Value-1, "attack");
			}else{
				EvalSurroundingTokenActions(unit, prevToken, unit.GetStat("AttackRange").Value, "attack");
			}
		}
		// Otherwise, the action must be attack, which elicits no further action once that range runs out
	}

	// Returns remainingRange if unit can move into this token based on terrainMod, negative means the unit can not move here
	// Note - you can move through your own units so don't return negative
	private float EvalToken(string unitName, Token token, float range, string action) {
		if(token.CurrentUnit != null && action == "move") {
			if(!token.CurrentUnit.MyTeam) {
				return -1f;
			}
		}
		float terrainWeight = GameData.TerrainWeight(unitName, token.CurrentTerrain.shortName);
		if(terrainWeight == 99f) {
			return -1;
		}
		float remainingRange = (action == "move")? range - terrainWeight : range - 1;
		if(remainingRange >= 0f) {
			if(token.CurrentUnit != null) {
				if(token.CurrentUnit.MyTeam) {
					return remainingRange;
				}
			}
			// Else if no unit, just add the action to the list
			AddValidAction(action, token);
		}
		return remainingRange;
	}

	// Clears the token vars and actions list
	private void ClearValidActions() {
		foreach(ValidAction action in Actions) {
			Tokens[action.col][action.row].SetActionProperties("clear");
		}
		Actions.Clear();
	}

	// Adds the specified action to the token and list - Move overwrites Attack
	private void AddValidAction(string act, Token token) {
		if(!token.CanMove && !token.CanAttack) {
			Actions.Add(CreateValidAction(act, token));
		}else if(act == "move" && token.CanAttack){
			RemoveValidAction(token);
			Actions.Add(CreateValidAction(act, token));
		}
	}

	// Sets up for overwrite and removes the action from a token
	private void RemoveValidAction(Token token) {
		// We don't have a reference to the specific action so loop through valid actions
		for(int index = 0; index < Actions.Count; index++) {
			ValidAction currAction = Actions[index];
			if(currAction.col == token.X && currAction.row == token.Y) {
				Actions.Remove(currAction);
				token.SetActionProperties("overwrite");
			}
		}
	}

	// Creates the action and set the token properties
	private ValidAction CreateValidAction(string act, Token token) {
		ValidAction action;
		action.action = act;
		action.col = token.X;
		action.row = token.Y;
		token.SetActionProperties(act);
		return action;
	}



#region Development
	// For testing - any initial variable setting
	private void TestStartup() {
		//PlayerPrefs.DeleteAll();
		//PlayerPrefs.DeleteKey("session");
		//GridAlpha = "33";
	}

	private void TestServer() {
		// Start the websocket connection
		Server.Connect();
		// Login testUser. If doesn't exist, create user and login
		if(PlayerPrefs.HasKey("session")) {
			if(!Server.RetryLogin()) {
				// You probably cleared your used from the table but kept the session token
				PlayerPrefs.DeleteKey("session");
				Debug.Log("deleted old session - restart game");
			}
		}else if(!Server.Login("testUser", "tactics")) {
			Debug.Log("Login failed, creating user...");
			Server.CreateUser("testUser", "tactics", "tactics@gmail.com");
			Server.Login("testUser", "tactics");
		}
		// Once logged in, get user info and load static data
		Server.GetUserInfo();
		Server.InitialLoad();
	}

	// For testing - gameplay variables and functionality
	private void TestGamePlay() {
		// Create Grid and add test units
		SpawnController SC = gameObject.AddComponent<SpawnController>();
		Tokens = SC.CreateMap("Forest Pattern");
		Units.Add(Tokens[4][6].CurrentUnit = SC.CreateUnit("Warrior",4,6));
		Units.Add(Tokens[6][8].CurrentUnit = SC.CreateUnit("Warrior",6,8));
		Units.Add(Tokens[7][5].CurrentUnit = SC.CreateUnit("Warrior",7,5));
		Units.Add(Tokens[6][6].CurrentUnit = SC.CreateUnit("Warrior",6,6));
		Units[0].MyTeam = true;
		Units[1].MyTeam = true;
		Units[2].MyTeam = false;
		Units[3].MyTeam = false;

		// Create terrain weight map
		//TerrainMod.CreateWeightMap();
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

// Struct for unit's actions when clicked
public struct ValidAction {
	public string action;
	public int col;
	public int row;
}
