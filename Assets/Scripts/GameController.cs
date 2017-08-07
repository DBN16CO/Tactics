using UnityEngine;
using UnityEngine.SceneManagement;

using System.Collections.Generic;

public class GameController : MonoBehaviour {

	private static Token[][] _tokens;
	private static int _gridHeight;
	private static int _gridLength;

	private static List<Unit> _units;
	private static Token _selectedToken;

	// Collection of valid moves - Key is (x,y) coordinate, Value is UnitAction Enum Index
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
	public static Token IntendedTarget;
	public static GameController Main;

	// UI variables
	public GameObject EndTurnGO;
	public GameObject BackToMenuGO;
	public UnitInfoController UnitInfo;
	public UnitInfoController TargetInfo;

	private bool _endTurn;
	private bool _backToMenu;

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
		Main = this;
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
			InitializeUI();
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
		CommunicationManager.OnDisable();
	}

	// Run when turn starts to reset units, etc
	public void StartTurn() {
		foreach(Unit unit in Units) {
			if(unit.MyTeam) {
				unit.Reset();
			}
		}
	}

	// Token actions when unit is placed
	public void PlaceUnit(Token token) {
		token.CurrentUnit = SC.CreateUnit(UnitBeingPlaced.matchUnit,token.X,token.Y, true);
	}

	// Runs when a unit is selected. Take action if possible, otherwise show unit info
	public void SelectUnit(Token token) {
		Unit unit = token.CurrentUnit;
		ShowUnitInfo(unit);
		SelectedToken = token;
		if(unit.MyTeam && !unit.TakenAction && GameData.CurrentMatch.UserTurn) {
			SetValidActions(token);
		}
	}

	// Shows unit info on UI
	public void ShowUnitInfo(Unit unit) {
		UnitInfo.SetUnitInfo(unit.Info);
	}
	// Shows target info on UI
	public void ShowTargetInfo(Unit unit) {
		TargetInfo.SetUnitInfo(unit.Info);
	}

	// Runs when a unit is unselected (i.e. user clicks other unit, or unit takes turn)
	public void UnselectUnit() {
		UnitInfo.RemoveUnitInfo();
		SelectedToken = null;
		IntendedMove = null;
		UnselectTarget();
		ClearValidActions();
	}

	// Repaints the available actions after a unit's intended move is set
	public void PaintIntendedMoveActions() {
		foreach(KeyValuePair<Twople<int, int>, int> action in Actions) {
			Token currToken = Tokens[action.Key.Item1][action.Key.Item2];
			if(currToken == IntendedMove || CanTargetFromToken(currToken)) {
				continue;
			}
			currToken.SetActionProperties("clear");
		}
	}
	// Checks whether the unit can target from IntendedMove
	public bool CanTargetFromToken(Token currToken) {
		int _x = 0;
		int _y = 0;
		if((currToken.CanAttack && currToken.HasEnemy) || (currToken.CanHeal && currToken.HasAlly)) {
			_x = (IntendedMove != null)? Mathf.Abs(IntendedMove.X - currToken.X) : Mathf.Abs(SelectedToken.X - currToken.X);
			_y = (IntendedMove != null)? Mathf.Abs(IntendedMove.Y - currToken.Y) : Mathf.Abs(SelectedToken.Y - currToken.Y);
			int range = GameData.GetUnit(SelectedToken.CurrentUnit.Info.Name).GetStat("Attack Range").Value; 
			return range >= _x + _y;
		}
		return false;
	}

	// Move unit to new token and paint new actions
	public void SetIntendedMove(Token token) {
		UnselectTarget();
		IntendedMove = token;
		SelectedToken.CurrentUnit.transform.position = token.gameObject.transform.position;
		PaintIntendedMoveActions();
	}
	// Confirm move unit to new token and unselect after
	public void ConfirmMove() {
		if(Server.TakeNonTargetAction(SelectedToken.CurrentUnit,"Wait", IntendedMove.X, IntendedMove.Y)) {
			MoveUnit();
		}
	}
	// All the actions when moving a unit
	public void MoveUnit() {
		IntendedMove.CurrentUnit = SelectedToken.CurrentUnit;
		SelectedToken.CurrentUnit = null;
		IntendedMove.CurrentUnit.ConfirmMove();
	}
	// When your unit is already selected and you choose a target
	public void SetIntendedTarget(Token token) {
		if(IntendedMove == null) {
			// If targeting from current token, IntendedMove will be null so set it now
			SetIntendedMove(SelectedToken);
		}
		UnselectTarget();
		IntendedTarget = token;
		IntendedTarget.gameObject.GetComponent<SpriteRenderer>().color = HexToColor("000000FF");
		ShowTargetInfo(IntendedTarget.CurrentUnit);
	}
	public void UnselectTarget() {
		if(IntendedTarget != null) {
			IntendedTarget.gameObject.GetComponent<SpriteRenderer>().color = HexToColor("FFFFFFFF");
			TargetInfo.RemoveUnitInfo();
			IntendedTarget = null;
		}
	}
	// Confirms attack target and moves to intended token if applicable
	public void ConfirmTargetAction(Unit targetUnit) {
		Dictionary<string, object> unitDict;
		Dictionary<string, object> targetDict;
		// Below confirms whether the target token is red or green (attack or heal)
		string action = (IntendedTarget.CanAttack)? "Attack" : "Heal";
		if(Server.TakeTargetAction(SelectedToken.CurrentUnit, action, targetUnit.Info.ID, out unitDict, out targetDict, IntendedMove.X, IntendedMove.Y)) {
			// Update unit infos
			SelectedToken.CurrentUnit.UpdateInfo(int.Parse(unitDict["NewHP"].ToString()));
			targetUnit.UpdateInfo(int.Parse(targetDict["NewHP"].ToString()));
			if(SelectedToken.CurrentUnit.Info.HP <= 0) {
				SelectedToken.CurrentUnit.DestroyUnit();
				UnselectUnit();
			}
			if(targetUnit.Info.HP <= 0) {
				targetUnit.DestroyUnit();
			}
			MoveUnit();
		}
	}

	// Begins the process to assess valid moves for the selected unit
	// Set range to unit's remaining range (in case we make units able to move twice if it has leftover) - I think this concept should be removed (B)
	// After all actions have been assessed, paint the tokens
	private void SetValidActions(Token token) {
		// Reset valid actions and queue of remaining tokens to check
		ClearValidActions();

		// Info about the unit being checked
		Unit movingUnit = token.CurrentUnit;
		string unitName = movingUnit.name;
		int movementRemaining = token.CurrentUnit.RemainingMoveRange;

		// Attack range if the unit can attack or heal
		// As of now, for a unit that can do both, attack is determined first,
		// meaning that unoccupied valid targets will be red, not green
		int startingAttackRange = GameData.GetUnit(unitName).GetStat("Attack Range").Value;

		// Elements queued to be (or already) checked
		bool[][] queuedTokens  = JaggedArray.CreateJaggedArray<bool[][]>(GridLength,GridHeight);

		// Queue of elements to be processed, Tuple elements are:
		// Item1 - This token
		// Item2 - Remaining range (movement or attack/heal)
		PriorityQueue<Twople<Token, int> > uncheckedMoveTokens   = new PriorityQueue<Twople<Token, int> >();
		PriorityQueue<Twople<Token, int> > uncheckedAttackTokens = new PriorityQueue<Twople<Token, int> >();
		PriorityQueue<Twople<Token, int> > uncheckedHealTokens   = new PriorityQueue<Twople<Token, int> >();

		// Insert root token (unit's location) into the queue
		Twople<Token, int> firstToken = Twople.Create(token, movementRemaining);
		uncheckedMoveTokens.Enqueue(movementRemaining, firstToken);
		queuedTokens[token.X][token.Y] = true;

		// Declare while loop vars once
		Twople<Token, int> currElement;
		Twople<int, int> coord;
		int currX;
		int currY;
		int terrainWeight;
		Twople<int, int>[] neighbors = {
			Twople.Create( 0,  1),
			Twople.Create( 0, -1),
			Twople.Create( 1,  0),
			Twople.Create(-1,  0)
		};
		bool checkNeighbors = false;

		// Determmine if the unit can attack or heal before entering loop
		bool canAttack = GameData.GetUnit(unitName).GetAction("Attack");
		bool canHeal = GameData.GetUnit(unitName).GetAction("Heal");

		// List of valid actions that this unit can take, using the UnitActions Enum
		List<int> validActionIds = new List<int>();
		validActionIds.Add((int)UnitAction.move);
		if(canAttack){
			validActionIds.Add((int)UnitAction.attack);
		}
		if(canHeal){
			validActionIds.Add((int)UnitAction.heal);
		}

		PriorityQueue<Twople<Token, int> > currQueue;
		int phase;
		for(int i = 0; i<validActionIds.Count; i++){
			switch(validActionIds[i]){
				case (int)UnitAction.move:
					currQueue = uncheckedMoveTokens;
					phase = (int)UnitAction.move;
					break;
				case (int)UnitAction.attack:
					currQueue = uncheckedAttackTokens;
					phase = (int)UnitAction.attack;
					break;
				case (int)UnitAction.heal:
					currQueue = uncheckedHealTokens;
					phase = (int)UnitAction.heal;
					break;
				default:
					continue;
			}

			while(currQueue.Count != 0){
				// Process first element in queue
				currElement = currQueue.Dequeue();
				currX = currElement.Item1.X;
				currY = currElement.Item1.Y;
				coord = Twople.Create(currX, currY);

				if(currElement.Item2 >= 0){
					checkNeighbors = true;

					// During movement phase, can move onto self or unoccupied locations
					if(currElement.Item1.CurrentUnit == null ||
							currElement.Item1.CurrentUnit.Info.ID == movingUnit.Info.ID)
					{
						Actions.Add(coord, phase);
						currElement.Item1.SetActionProperties(((UnitAction)phase).ToString());
					}
					// Logic to handle a token with a unit:
					else if(currElement.Item1.CurrentUnit != null &&
							currElement.Item1.CurrentUnit.Info.ID != movingUnit.Info.ID)
					{
						// Logic for when the token is occupied by an ally
						if(currElement.Item1.CurrentUnit.MyTeam){
							// If still moving, add this to heal check for after movement is done
							switch(phase){
								case (int)UnitAction.move:
									if(currElement.Item2 == 0){
										checkNeighbors = false;
										if(canAttack){
											uncheckedAttackTokens.Enqueue(0, Twople.Create(
												Tokens[currX][currY], startingAttackRange-1)
											);
										}
										if(canHeal){
											uncheckedHealTokens.Enqueue(0, Twople.Create(
												Tokens[currX][currY], startingAttackRange-1)
											);
										}
									}
									if(canHeal){
										uncheckedHealTokens.Enqueue(0, Twople.Create(
											Tokens[currX][currY], startingAttackRange-1)
										);
									}
									break;
								// Can heal allies
								case (int)UnitAction.heal:
									Actions.Add(coord, (int)UnitAction.heal);
									currElement.Item1.SetActionProperties("heal");
									break;
							}
						}
						// Logic for when the token is occupied by an enemy
						else{
							// If still moving, add this to attack check for after movement is done
							switch(phase){
								case (int)UnitAction.move:
									if(currElement.Item2 == 0){
										checkNeighbors = false;
										if(canAttack){
											uncheckedAttackTokens.Enqueue(0, Twople.Create(
												Tokens[currX][currY], startingAttackRange-1)
											);
										}
										if(canHeal){
											uncheckedHealTokens.Enqueue(0, Twople.Create(
												Tokens[currX][currY], startingAttackRange-1)
											);
										}
									}
									if(canAttack){
										checkNeighbors = false;
										uncheckedAttackTokens.Enqueue(0, Twople.Create(
											Tokens[currX][currY], startingAttackRange-1)
										);
									}
									break;
								case (int)UnitAction.attack:
									Actions.Add(coord, (int)UnitAction.attack);
									currElement.Item1.SetActionProperties("attack");
									break;
							}
						}
					}

					// Add the 4 neighbors to the queue to be checked
					if(checkNeighbors){
						foreach(Twople<int, int> nbr in neighbors){
							if(currX + nbr.Item1 < GridLength && currX + nbr.Item1 >= 0 &&
							   currY + nbr.Item2 < GridHeight && currY + nbr.Item2 >= 0) {
								if(!queuedTokens[currX + nbr.Item1][currY + nbr.Item2]){
									queuedTokens[currX + nbr.Item1][currY + nbr.Item2] = true;

									// Movement remaining is existing remaining movement - terrain weight
									terrainWeight = GameData.TerrainWeight(unitName, Tokens[currX + nbr.Item1][currY + nbr.Item2].CurrentTerrain.shortName);
									movementRemaining = (phase == (int)UnitAction.move)?
									currElement.Item2 - terrainWeight: currElement.Item2 - 1;

									currQueue.Enqueue(movementRemaining, Twople.Create(
										Tokens[currX + nbr.Item1][currY + nbr.Item2],
										movementRemaining
									));
								}
							}
						}
					}	
				}
				// Out of moves, switch to attacking
				else if(phase == (int)UnitAction.move && canAttack){
					uncheckedAttackTokens.Enqueue(0, Twople.Create(
						Tokens[currX][currY], startingAttackRange-1)
					);
				}
				// Out of moves, switch to healing
				else if(phase == (int)UnitAction.move && canHeal){
					uncheckedHealTokens.Enqueue(0, Twople.Create(
						Tokens[currX][currY], startingAttackRange-1)
					);
				}
			}
		}

		foreach(KeyValuePair<Twople<int, int>, int> action in Actions) {
			Tokens[action.Key.Item1][action.Key.Item2].PaintAction(((UnitAction)action.Value).ToString());
		}
	}

	// Clears the token vars and actions list
	private void ClearValidActions() {
		foreach(KeyValuePair<Twople<int, int>, int> action in Actions) {
			Tokens[action.Key.Item1][action.Key.Item2].SetActionProperties("clear");
		}
		Actions.Clear();
	}

	public void ConfirmEndTurn() {
		if(!_endTurn) {
			EndTurnGO.transform.Find("Confirm").gameObject.SetActive(true);
			_endTurn = true;
		}
	}
	public void EndTurn() {
		if(Server.EndTurn()) {
			_endTurn = false;
			GameData.CurrentMatch.UserTurn = false;
			EndTurnGO.transform.Find("Confirm").gameObject.SetActive(false);
			EndTurnGO.SetActive(false);
		}
	}
	public void CancelEndTurn() {
		_endTurn = false;
		EndTurnGO.transform.Find("Confirm").gameObject.SetActive(false);
	}

	// Initializes the game UI when opening after place units has already been completed
	private void InitializeUI() {
		EndTurnGO.transform.Find("Confirm").gameObject.SetActive(false);
		BackToMenuGO.SetActive(false);
		_endTurn = false;
		_backToMenu = false;
		if(!GameData.CurrentMatch.UserTurn) {
			EndTurnGO.SetActive(false);
		}
	}

	// Initializes the game map when opening after place units has already been completed
	private void InitializeMap() {
		foreach(MatchUnit unit in myUnits) {
			if(unit.X != -1 && unit.HP > 0) {
				SC.CreateUnit(unit, unit.X, unit.Y, true);
			}
		}
		foreach(MatchUnit unit in enemyUnits) {
			if(unit.X != -1 && unit.HP > 0) {
				SC.CreateUnit(unit, unit.X, unit.Y, false);
			}
		}
	}

	public void ConfirmBackToMenu() {
		if(!_backToMenu) {
			BackToMenuGO.SetActive(true);
			_backToMenu = true;
		}
	}
	// Returns user to the main menu
	public void BackToMenu() {
		SceneManager.LoadSceneAsync("MainMenu", LoadSceneMode.Single);
	}
	public void CancelBackToMenu() {
		_backToMenu = false;
		BackToMenuGO.SetActive(false);
	}

	public static Color HexToColor(string hex) {
		hex = hex.Replace ("0x", "");//in case the string is formatted 0xFFFFFF
		hex = hex.Replace ("#", "");//in case the string is formatted #FFFFFF
		byte a = 255;//assume fully visible unless specified in hex
		byte r = byte.Parse(hex.Substring(0,2), System.Globalization.NumberStyles.HexNumber);
		byte g = byte.Parse(hex.Substring(2,2), System.Globalization.NumberStyles.HexNumber);
		byte b = byte.Parse(hex.Substring(4,2), System.Globalization.NumberStyles.HexNumber);
		//Only use alpha if the string has enough characters
		if(hex.Length == 8){
			a = byte.Parse(hex.Substring(6,2), System.Globalization.NumberStyles.HexNumber);
		}
		return new Color32(r,g,b,a);
	}

#region Development
	// Runs every frame
	void Update() {
		// Computer move/zoom
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
		if(Input.GetKey("o"))

		{
			Camera.main.orthographicSize /= 0.95f;
		}
		// if(!GameData.CurrentMatch.UserTurn) {
		// 	_qguTimer += Time.deltaTime;
		// 	if(_qguTimer >= _qguInterval) {
		// 		CheckForTurn();
		// 		_qguTimer = 0f;
		// 	}
		// }
		Queue<Dictionary<string, object>> asyncMessages = CommunicationManager.GetAsyncKeyQueue("ACTION_TAKEN");
		while(asyncMessages != null && asyncMessages.Count > 0){
			Dictionary<string, object> currentMessage = asyncMessages.Dequeue();

			// If the current message pertains to the active game
			if(currentMessage["Game"] != null && string.Compare((string)currentMessage["Game"], GameData.CurrentMatch.Name) == 0){

			}
		}
	}

	// Loads active games
	private void CheckForTurn() {
		if(!(bool)Server.QueryGames()["Success"]) {
			UnityEngine.Debug.Log("Query Games failed");
			return;
		}
		int _matchID = GameData.CurrentMatch.MatchID;
		if(GameData.GetMatches[_matchID].UserTurn) {
			UnityEngine.Debug.Log("It's now your turn");
			GameData.CurrentMatch = GameData.GetMatches[_matchID];
			SceneManager.LoadSceneAsync("Game", LoadSceneMode.Single);
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

enum UnitAction{ move = 0, attack = 1, heal = 2, none = 3 };
