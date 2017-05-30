using UnityEngine;
using System.Collections.Generic;
using System.Diagnostics;
using System;

public class GameController : MonoBehaviour {

	private static Token[][] _tokens;
	private static int _gridHeight;
	private static int _gridLength;

	private static List<Unit> _units;
	private static Token _selectedToken;
	//private List<ValidAction> _actions;		// Array of valid moves
	// Collection of valid moves
	private Dictionary<Twople<int, int>, int> _actions;

	// Game vars
	private MapData _currentMap;
	public List<MatchUnit> myUnits;
	public List<MatchUnit> enemyUnits;
	public int myTeam;


	// Static Game vars
	public static SpawnController SC;
	public static PlaceUnitsController PU;
	public static bool PlacingUnits;
	public static PUUnit UnitBeingPlaced;
	public static Token IntendedMove;		// If the player has selected a token to move to but hasn't confirmed the move yet


	// vars for development
	private bool _endTurn;
	public static long count;


#region Setters and Getters
	public static Token[][] Tokens {
		get{return _tokens;}
		set{_tokens = value;}
	}
	public static int GridHeight {
		get{return _gridHeight;}
		set{_gridHeight = value;}
	}
	public static int GridLength {
		get{return _gridLength;}
		set{_gridLength = value;}
	}
	public static List<Unit> Units {
		get{return _units;}
		set{_units = value;}
	}
	public static Token SelectedToken {
		get{return _selectedToken;}
		set{_selectedToken = value;}
	}
	//public List<ValidAction> Actions {
	public Dictionary<Twople<int, int>, int> Actions {
		get{return _actions;}
		set{_actions = value;}
	}
	public MapData CurrentMap {
		get{return _currentMap;}
		set{_currentMap = value;}
	}

	// When Conditions
	private bool UnitsArePlaced {
		get{
			foreach(MatchUnit unit in myUnits) {
				if(unit.X == -1) {
					return false;
				}
			}
			return true;
		}
	}

#endregion


	// Ultimately, this will run on match generation
	// Development - place anything we need to initialize for dev/test here
	void Start() {
		// Initialize match variables
		Actions = new Dictionary<Twople<int, int>, int>();
		Units = new List<Unit>();
		SC = gameObject.AddComponent<SpawnController>();
		// Map game vars from QGU match data and determine if place units is necessary
		myTeam = GameData.CurrentMatch.UserTeam;
		myUnits = GameData.CurrentMatch.AlliedUnits;
		enemyUnits = GameData.CurrentMatch.EnemyUnits;
		PlacingUnits = !UnitsArePlaced;
		_currentMap = GameData.GetMap(GameData.CurrentMatch.MapName);
		SC.CreateMap(GameData.CurrentMatch.MapName);
		if(PlacingUnits) {
			PU = (Instantiate(Resources.Load("Prefabs/PlaceUnits"),GameObject.Find("Canvas").GetComponent<Canvas>().transform) as GameObject).GetComponent<PlaceUnitsController>();
		}else{
			InitializeMap();
			StartTurn();
		}



		// Block for testing -------------------------------------------
		// For any gameplay vars and functions
//		TestGamePlay();
		// End testing block -------------------------------------------
	}

	// Runs when the app is closed - attempt to close the websocket cleanly
	void OnApplicationQuit() {
		Server.Disconnect();
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
	public void SelectUnit(Token token) {
		Unit unit = token.CurrentUnit;
		SelectedToken = token;
		if(unit.MyTeam && !unit.TakenAction && GameData.CurrentMatch.UserTurn) {
			SetValidActions(token);
		}else{
			ShowUnitInfo(unit);
		}
	}

	// Placeholder for what will contain code to show unit's info on UI
	public void ShowUnitInfo(Unit unit) {
		UnityEngine.Debug.Log(((unit.MyTeam)? "Your " : "Opponent's ") + unit.Info.Name);
	}

	// Runs when a unit is unselected (i.e. user clicks other unit, or unit takes turn)
	public void UnselectUnit() {
		SelectedToken = null;
		ClearValidActions();
	}

	// Begins the process to asses valid moves for the selected unit
	// Set range to unit's remaining range (in case we make units able to move twice if it has leftover)
	// After all actions have been assessed, paint the tokens
	private void SetValidActions(Token token) {
		Stopwatch timePerParse = Stopwatch.StartNew();

		// Reset valid actions and queue of remaining tokens to check
		ClearValidActions();

		// Info about the unit beinc checked
		Unit movingUnit = token.CurrentUnit;
		string unitName = movingUnit.name;

		// Initial movement remaining is root token weight + total move range
		// since the weight will be subtracted within while loop
		float terrainWeight = GameData.TerrainWeight(unitName, token.CurrentTerrain.shortName);
		float movementRemaining = token.CurrentUnit.RemainingMoveRange;

		// HashSet of elements already checked, the int is X + (Length * Y)
		HashSet<int> checkedTokens = new HashSet<int>();
		HashSet<int> queuedTokens = new HashSet<int>();

		// Queue of elements to be processed, Tuple elements are:
		// Item1 - This token
		// Item2 - Remaining movement
		// Item3 - UnitAction ID (move or attack)
		Queue<Threeple<Token, float, int> > uncheckedTokens = new Queue<Threeple<Token, float, int> >();

		// Insert root token (unit's location) into the queue
		Threeple<Token, float, int> firstToken = Threeple.Create(token, movementRemaining + terrainWeight, (int)UnitAction.move);
		uncheckedTokens.Enqueue(firstToken);

		// Declare while loop vars once
		Threeple<Token, float, int> currElement;
		Twople<int, int> coord;
		int newCoord;
		int currX;
		int currY;
		Twople<int, int>[] neighbors = {
			Twople.Create( 0,  1),
			Twople.Create( 0, -1),
			Twople.Create( 1,  0),
			Twople.Create(-1,  0)
		};

		while(uncheckedTokens.Count != 0){
			count++;
			// Process first element in queue
			currElement = uncheckedTokens.Dequeue();
			currX = currElement.Item1.X;
			currY = currElement.Item1.Y;
			coord = Twople.Create(currX, currY);
			
			// Movement remaining is existing remaining movement - terrain weight
			terrainWeight = GameData.TerrainWeight(unitName, currElement.Item1.CurrentTerrain.shortName);
			movementRemaining = currElement.Item2 - terrainWeight;

			// If the current token is occupied by an enemy, cannot move here
			if(currElement.Item1.CurrentUnit != null && currElement.Item3 == (int)UnitAction.move && !currElement.Item1.CurrentUnit.MyTeam) {

			}
			// If movement remaining is not negative, can move here
			else if(movementRemaining >= 0){
				// Cannot move onto ally
				if(currElement.Item1.CurrentUnit == null ||
					currElement.Item1.CurrentUnit.Info.ID == movingUnit.Info.ID){
					Actions.Add(coord, currElement.Item3);
					currElement.Item1.SetActionProperties(((UnitAction)currElement.Item3).ToString());
				}

				// Add the 4 neighbors to the queue to be checked
				foreach(Twople<int, int> nbr in neighbors){
					if(currX + nbr.Item1 < GridLength && currX + nbr.Item1 >= 0 &&
					   currY + nbr.Item2 < GridHeight && currY + nbr.Item2 >= 0) {
						newCoord = currX + nbr.Item1 + (GridLength * (currY + nbr.Item2));
						if(!checkedTokens.Contains(newCoord) && !queuedTokens.Contains(newCoord)){
							queuedTokens.Add(newCoord);
							uncheckedTokens.Enqueue(Threeple.Create(
								Tokens[currX + nbr.Item1][currY + nbr.Item2],
								movementRemaining, currElement.Item3
							));
						}
					}
				}
			}
			// Else, cannot move to neighbors either
			//TODO: attacking
			else{
				//continue;
			}

			// Do not check this token again
			checkedTokens.Add(currX + (GridLength * currY));
		}

		long ticksThisTime = timePerParse.ElapsedTicks;
		long msThisTime = timePerParse.ElapsedMilliseconds;

		UnityEngine.Debug.Log("Count:" + count);
		UnityEngine.Debug.Log("Ticks:" + ticksThisTime);
		UnityEngine.Debug.Log("MS:" + msThisTime);


		foreach(KeyValuePair<Twople<int, int>, int> action in Actions) {
			Tokens[action.Key.Item1][action.Key.Item2].PaintAction(((UnitAction)action.Value).ToString());
		}
	}
/*
	// Evaluates the surrounding tokens for valid actions
	private void EvalSurroundingTokenActions(Unit unit, Token token, float range, string action) {
		count++;
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
				EvalSurroundingTokenActions(unit, prevToken, GameData.GetUnit(unit.name).GetStat("Attack Range").Value-1, "attack");
			}else{
				EvalSurroundingTokenActions(unit, prevToken, GameData.GetUnit(unit.name).GetStat("Attack Range").Value, "attack");
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
		for(int x = 0; x < Actions.Count; x++) {
			ValidAction currAction = Actions[x];
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
*/
	// Clears the token vars and actions list
	private void ClearValidActions() {
		foreach(KeyValuePair<Twople<int, int>, int> action in Actions) {
			Tokens[action.Key.Item1][action.Key.Item2].SetActionProperties("clear");
		}
		Actions.Clear();
	}

	// Initializes the game map when opening after place units has already been completed
	private void InitializeMap() {
		foreach(MatchUnit unit in myUnits) {
			if(unit.X != -1) {
				SC.CreateUnit(unit, unit.X, unit.Y, true);
			}
		}
		foreach(MatchUnit unit in enemyUnits) {
			if(unit.X != -1) {
				SC.CreateUnit(unit, unit.X, unit.Y, false);
			}
		}
	}



#region Development
	// For testing - gameplay variables and functionality
	private void TestGamePlay() {
		// Create Grid and add test units
		//SC = gameObject.AddComponent<SpawnController>();

		// Testing for place units
		/*myTeam = 2;
		myUnits = new List<MatchUnit>();
		for(int cnt = 0; cnt < 8; cnt++) {
			MatchUnit unit = new MatchUnit();
			switch(cnt) {
				case 0: unit.Name = "Archer"; 	break;
				case 1: unit.Name = "Archer"; 	break;
				case 2: unit.Name = "Mage";		break;
				case 3: unit.Name = "Cleric"; 	break;
				case 4: unit.Name = "Armor"; 	break;
				case 5: unit.Name = "Armor"; 	break;
				case 6: unit.Name = "Armor";	break;
				case 7: unit.Name = "Armor"; 	break;
			}
			unit.X = -1; unit.Y = -1;
			myUnits.Add(unit);
		}
		MatchLeader myLeader = new MatchLeader();
		myLeader.Name = "Sniper";

		PlacingUnits = !UnitsArePlaced;

		string mapName = "Forest Pattern";
		_currentMap = GameData.GetMap(mapName);
		Tokens = SC.CreateMap(mapName);

		PU = (Instantiate(Resources.Load("Prefabs/PlaceUnits"),GameObject.Find("Canvas").GetComponent<Canvas>().transform) as GameObject).GetComponent<PlaceUnitsController>();*/

		/*
		Units.Add(Tokens[4][6].CurrentUnit = SC.CreateUnit("Warrior",4,6));
		Units.Add(Tokens[6][8].CurrentUnit = SC.CreateUnit("Warrior",6,8));
		Units.Add(Tokens[7][5].CurrentUnit = SC.CreateUnit("Warrior",7,5));
		Units.Add(Tokens[6][6].CurrentUnit = SC.CreateUnit("Warrior",6,6));
		Units[0].MyTeam = true;
		Units[1].MyTeam = true;
		Units[2].MyTeam = false;
		Units[3].MyTeam = false;*/

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
		if(Input.GetKeyDown("e")){
			if(GameData.CurrentMatch.UserTurn) {
				_endTurn = true;
				UnityEngine.Debug.Log("Press 'y' to confirm endturn, otherwise press 'n'");
			}else {
				UnityEngine.Debug.Log("It's not your turn to end...");
			}
		}
		if(_endTurn) {
			if(Input.GetKeyDown("y")) {
				if(Server.EndTurn()) {
					UnityEngine.Debug.Log("Turn ended");
				}
				_endTurn = false;
			}else if(Input.GetKeyDown("n")) {
				_endTurn = false;
				UnityEngine.Debug.Log("Endturn canceled");
			}
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

enum UnitAction{ move = 0, attack = 1, none = 2 };
