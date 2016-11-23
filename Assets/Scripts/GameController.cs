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

	// Runs when a unit is selected
	public void SelectUnit(Unit unit, Token token) {
		SelectedToken = token;
		if(unit.MyTeam && !unit.TakenAction) {
			// If your unit hasn't taken its turn
			SetValidActions(unit, token);
		}else{
			// Else show info (also includes enemy units)
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
	private void SetValidActions(Unit unit, Token token) {
		// Set range to unit's remaining range (in case we make units able to move twice if it has leftover)
		float range = unit.RemainingMoveRange;
		// Add token unit is currently standing on, because looks better
		AddValidAction("move", token);
		// Evaluate surrounding tokens, starting with the token the selected unit is on
		EvalSurroundingTokenActions(unit, token, range, "move");

		// After all actions have been assessed, paint the tokens
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
	private void EvalNextToken(Unit unit, Token token, Token prevToken, float range, string action) {
		// Evaluate this token for valid actions, and calculate remaining range, if any
		float remainingRange;
		remainingRange = EvalToken(unit.name, token, range, action);
		if(remainingRange >= 0f) {
			// If there is range remaining, evaluate surrounding tokens with whatever the current action is (move or attack)
			EvalSurroundingTokenActions(unit, token, remainingRange, action);
		}else if(action == "move") {
			// If there is no range remaining (i.e. the unit can NOT move into this token)
			// and the action is currently "move"
			if(prevToken.CurrentUnit != null) {
				// We can't move here (remainingrange is less than 0)
				// We also can't move to the previous token because prevToken.CurrentUnit != null
				// So we need to evaluate the tokens surrounding the PREVIOUS token
				// Use AtkRange-1 because the previous token uses the first tick of attack range
				// If we saved the previous previous token, we could eval surrounding with AtkRange
				EvalSurroundingTokenActions(unit, prevToken, unit.GetStat("AttackRange").Value-1, "attack");
			}else{
				// We still can't move here (remainingrange is less than 0)
				// This time, there's no unit in the previous token so start attack action from there
				EvalSurroundingTokenActions(unit, prevToken, unit.GetStat("AttackRange").Value, "attack");
			}
		}
		// Otherwise, the action must be attack, which elicits no further action once that range runs out
	}

	// Specifically evaluates the valid action of the token
	private float EvalToken(string unitName, Token token, float range, string action) {
		// If "move" action and current token contains an enemy unit, return -1 (stop movement)
		// This doesn't apply to our own team because units can move through those on their own team
		if(token.CurrentUnit != null && action == "move") {
			if(!token.CurrentUnit.MyTeam) {
				return -1f;
			}
		}
		// subtract from remainingrange based on TerrainMod if moving, or simply -1 if attacking
		float remainingRange = (action == "move")? range - TerrainMod.TerrainWeight(unitName, token.name) : range - 1;
		// If remainingrange > 0 (can potentially move further) and there's a unit on our team
		// Don't add movement action since you can't move to a token your unit is on
		// Return positive remainingRange to continue movement check
		if(remainingRange >= 0f) {
			if(token.CurrentUnit != null) {
				if(token.CurrentUnit.MyTeam) {
					return remainingRange;
				}
			}
			// Else if no unit, add the action to the list
			AddValidAction(action, token);
		}
		return remainingRange;
	}

	// Clears the list of actions
	private void ClearValidActions() {
		foreach(ValidAction action in Actions) {
			// Clear the CanMove or CanAttack vars off the tokens
			Tokens[action.col][action.row].SetActionProperties("clear");
		}
		// Clear the list
		Actions.Clear();
	}

	// Adds the specified action to the token and list
	private void AddValidAction(string act, Token token) {
		if(!token.CanMove && !token.CanAttack) {
			// If no actions on the token yet, just add
			Actions.Add(CreateValidAction(act, token));
		}else if(act == "move" && token.CanAttack){
			// Move overwrites Attack, so remove and add
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
				// Remove from list and overwrite token properties
				// The parameter 'overwrite' was created because 'clear' also repaints the token
				// I don't want to remove the attack paint then add move paint
				// Overwrite simply clears CanMove / CanAttack
				Actions.Remove(currAction);
				token.SetActionProperties("overwrite");
			}
		}
	}

	// Creates the action
	private ValidAction CreateValidAction(string act, Token token) {
		ValidAction action;
		action.action = act;
		action.col = token.X;
		action.row = token.Y;
		// Set token properties (CanMove/CanAttack)
		token.SetActionProperties(act);
		return action;
	}



#region Development
	// For testing - any initial variable setting
	private void TestStartup() {
		//PlayerPrefs.DeleteAll();
		//PlayerPrefs.DeleteKey("session");
		GridAlpha = "33";
	}

	private void TestServer() {
		// Start the websocket connection
		Server.Connect();
		// Login testUser. If doesn't exist, create user and login
		if(PlayerPrefs.HasKey("session")) {
			Server.RetryLogin();
		}else if(!Server.Login("testUser", "tactics")) {
			Debug.Log("Login failed, creating user...");
			Server.CreateUser("testUser", "tactics", "tactics@gmail.com");
			Server.Login("testUser", "tactics");
		}
	}

	// For testing - gameplay variables and functionality
	private void TestGamePlay() {
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

// Struct for unit's actions when clicked
public struct ValidAction {
	public string action;
	public int col;
	public int row;
}
