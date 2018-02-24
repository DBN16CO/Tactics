using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using System.Collections.Generic;
using System;

public class GameController : ParentController {

	/* Public Constant Game Variables */
	// None

	/* Private Constant Game Variables */
	private const bool GC_ALLY_TEAM = true;					// Constant for allied team
	private const bool GC_ENEMY_TEAM = false;				// Constant for enemy team
	private static readonly Twople<int, int>[] GC_NEIGHBORS = {	// The immediate cardinal direction neighbor offsets
		Twople.Create( 0,  1),									// for any given token.
		Twople.Create( 0, -1),
		Twople.Create( 1,  0),
		Twople.Create(-1,  0)
	};

	/* Public Static Game Variables */
	public static SpawnController SC;						// Reference to SpawnController
	public static PlaceUnitsController PU;					// Reference to PlaceUnitsController
	public static bool PlacingUnits;						// True if still in the Place Units phase
	public static PUUnit UnitBeingPlaced;					// Unit selected in PU tab, will be placed on clicked token
	public static Token IntendedMove;						// Selected a token to move to before actually moving
	public static Token IntendedTarget;						// Target selected by a targeted action

	public static GameObject MapTokens;						// All tokens should be placed under this as children
	public static GameObject MapUnits;						// All units should be placed under this as children
	public static GameObject MovementArrows;				// Parent for the icons displayed before a unit moves

	// UI variables
	public static RectTransform ErrorMessagePopup;			// Popup which displays error messages received from server
	public static int ERR_TEXT_IDX = 1;						// Child index of ErrorMessagePopup that is Text component
	public GameObject EndTurnGO;
	public GameObject BackToMenuGO;
	public static UnitInfoController _unitInfoController;	// Displays info of acting unit
	public static UnitInfoController _targetInfoController;	// Displays info if targeted unit

	public static GameController Main;						// Set to GameController instance

	/* Private Static Game Variables */
	// Grid data
	private static Token[][] _tokens;						// The grid of clickable tokens
	private static int _gridLength;							// The width (x-value) of the grid
	private static int _gridHeight;							// The height (y-value) of the grid
	private static Token _selectedToken;					// The last token touched by a user
	private static MapData _currentMap;						// Info on the map used for this game
	private Dictionary<int, Dictionary<int, int>> _actions;	// Collection of valid moves X --> (Y --> UnitAction enum)
	private static float _orthoSize;
	private static float _scale;

	// Unit data
	private static List<Unit> _units;						// All units in the game (ally and enemy)
	private static Dictionary<int, Unit> _alliedUnits;		// All allied units Unit ID --> Unit object
	private static Dictionary<int, Unit> _enemyUnits;		// All enemy units Unit ID --> Unit object
	public int myTeam;

	// Game vars
	private bool _displayEndTurn;							// If true, "End Turn" button is displayed
	private bool _displayBackToMenu;						// If true, "Back to Menu" button is displayed

#region Setters and Getters
	public static Token[][] Tokens {
		get{return _tokens;}
		set{_tokens = value;}
	}
	public static int GridLength {
		get{return _gridLength;}
		set{_gridLength = value;}
	}
	public static int GridHeight {
		get{return _gridHeight;}
		set{_gridHeight = value;}
	}
	public static List<Unit> Units {
		get{return _units;}
	}
	public static Dictionary<int, Unit> AlliedUnits{
		get{return _alliedUnits;}
	}
	public static Dictionary<int, Unit> EnemyUnits{
		get{return _enemyUnits;}
	}
	public static Token SelectedToken {
		get{return _selectedToken;}
		set{_selectedToken = value;}
	}
	public MapData CurrentMap {
		get{return _currentMap;}
		set{_currentMap = value;}
	}

#endregion

// ---------------------------------------------------------------------------------------------------------------------
// Unity Functions -----------------------------------------------------------------------------------------------------
	// Runs on match generation
	void Start() {
		// Initialize match variables
		_actions = new Dictionary<int, Dictionary<int, int>>();
		_units = new List<Unit>();
		SC = gameObject.AddComponent<SpawnController>();
		_unitInfoController = GameObject.Find("UnitInfo").GetComponent<UnitInfoController>();
		_targetInfoController = GameObject.Find("TargetInfo").GetComponent<UnitInfoController>();
		_currentMap = GameData.GetMap(GameData.CurrentMatch.MapName);
		Main = this;

		// Organize Grid elements in parent objects
		MapTokens = new GameObject();
		MapTokens.name = "MapTokens";
		MovementArrows = new GameObject();
		MovementArrows.name = "MovementArrows";
		MapUnits = new GameObject();
		MapUnits.name = "MapUnits";

		// Map game vars from QGU match data and determine if place units is necessary
		myTeam = GameData.CurrentMatch.UserTeam;
		_alliedUnits = new Dictionary<int, Unit>();
		_enemyUnits = new Dictionary<int, Unit>();
		PlacingUnits = !UnitsArePlaced(GC_ALLY_TEAM);

		SC.CreateMap(GameData.CurrentMatch.MapName);
		InitializeUI();

		if(PlacingUnits) {
			UnityEngine.Object puObj = Instantiate(Resources.Load("Prefabs/PlaceUnits"), GameObject.Find("Canvas").GetComponent<Canvas>().transform);
			PU = (puObj as GameObject).GetComponent<PlaceUnitsController>();
		}
		else{
			InitializeMap();
		}
	}

	// Runs every frame this controller is active
	void Update() {

#region development
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
		if(Input.GetKey("o"))		{
			Camera.main.orthographicSize /= 0.95f;
		}
#endregion

		/*
		 * Check if there were any server messages from the other player
		 */
		// If the other user has taken an action
		Queue<Dictionary<string, object>> asyncMessages = CommunicationManager.GetAsyncKeyQueue("ACTION_TAKEN");
		Dictionary<string, object> unit, target;

		while(asyncMessages != null && asyncMessages.Count > 0){
			Dictionary<string, object> currentMessage = asyncMessages.Dequeue();
			Dictionary<string, object> data = (Dictionary<string, object>)currentMessage["Data"];

			// A game ID and unit must be provided
			if(!data.ContainsKey("Game_ID") || !data.ContainsKey("Unit")){
				continue;
			}

			int key = int.Parse(data["Game_ID"].ToString());
			unit = (Dictionary<string, object>)data["Unit"];
			target = (data.ContainsKey("Target"))? (Dictionary<string, object>)data["Target"]: null;

			GameData.UpdateTAGameData(key, unit, target);

			if(key == GameData.CurrentMatch.ID){
				GameData.CurrentMatch = GameData.GetMatch(key);
				SceneManager.LoadSceneAsync("Game", LoadSceneMode.Single);
			}
		}

		// Check if the other user ended their turn
		asyncMessages = CommunicationManager.GetAsyncKeyQueue("ENDED_TURN");
		while(asyncMessages != null && asyncMessages.Count > 0){
			Dictionary<string, object> currentMessage = asyncMessages.Dequeue();
			Dictionary<string, object> data = (Dictionary<string, object>)currentMessage["Data"];

			// A game ID must be provided
			if(!data.ContainsKey("Game_ID")){
				continue;
			}

			int gameID = int.Parse(data["Game_ID"].ToString());
			GameData.UpdateETGameData(gameID);

			if(gameID == GameData.CurrentMatch.ID){
				GameData.CurrentMatch = GameData.GetMatch(gameID);
				ChangeTurn();
				EndTurnGO.SetActive(true);
			}
		}
	}

// ---------------------------------------------------------------------------------------------------------------------
// On Click Functions --------------------------------------------------------------------------------------------------
	/* Confirming the user wants to end their turn */
	public void ConfirmEndTurn() {
		if(!_displayEndTurn) {
			EndTurnGO.transform.Find("Confirm").gameObject.SetActive(true);
			_displayEndTurn = true;
		}
	}

	/* Confirming the user wants to exit this game */
	public void ConfirmBackToMenu() {
		if(!_displayBackToMenu) {
			BackToMenuGO.SetActive(true);
			_displayBackToMenu = true;
		}
	}

	/* Makes the server call to end the turn for this player */
	private void EndTurn() {
		Dictionary<string, object> response = Server.EndTurn();
		if(Parse.Bool(response["Success"])){
			_displayEndTurn = false;
			GameData.CurrentMatch.EndTurn();
			EndTurnGO.transform.Find("Confirm").gameObject.SetActive(false);
			EndTurnGO.SetActive(false);
			ChangeTurn();
		}
		else{
			GameController.DisplayGameErrorMessage(Parse.String(response["Error"]));
		}
	}

	/* Cancels ending the user's turn, closing the end turn confirm dialog box */
	public void CancelEndTurn() {
		_displayEndTurn = false;
		EndTurnGO.transform.Find("Confirm").gameObject.SetActive(false);
	}

	/* Closes the error message popup */
	public void CloseErrorMessage() {
		GameController.ErrorMessagePopup.gameObject.SetActive(false);
	}

	/* Returns user to the main menu */
	public void BackToMenu() {
		SceneManager.LoadSceneAsync("MainMenu", LoadSceneMode.Single);
	}

	/* Closes dialog asking user if they really want to exit to main menu */
	public void CancelBackToMenu() {
		_displayBackToMenu = false;
		BackToMenuGO.SetActive(false);
	}

// ---------------------------------------------------------------------------------------------------------------------
// Public Functions ----------------------------------------------------------------------------------------------------
	/**
	 * Checks whether the target is in range to counter
	 * <returns>True if the target can counter the attacking unit</returns>
	 */
	public static bool CanTargetCounter() {
		int _deltaX = (IntendedMove != null)? Mathf.Abs(IntendedMove.X - IntendedTarget.X) : Mathf.Abs(SelectedToken.X - IntendedTarget.X);
		int _deltaY = (IntendedMove != null)? Mathf.Abs(IntendedMove.Y - IntendedTarget.Y) : Mathf.Abs(SelectedToken.Y - IntendedTarget.Y);
		int range = GameData.GetUnit(IntendedTarget.CurrentUnit.UnitName).GetStat("Attack Range").Value;
		return range >= _deltaX + _deltaY;
	}

	/**
	 * Called when Token's OnMouseDown is triggered
	 * <param name="token">The token clicked to trigger the OnMouseDown event</param>
	 */
	public void HandleTokenClick(Token token){
		// During the Place Units phase
		if(PlacingUnits) {
			if(!token.IsDisabled() && token.CurrentUnit == null && UnitBeingPlaced != null) {
				PlaceUnit(token);
			}
			else if(token.CurrentUnit != null && UnitBeingPlaced == null) {
				SpawnController.ReturnPlacedUnit(token.CurrentUnit);
			}
			return;
		}

		/*
		 * Normal actions if not placing units
		 */
		// Performing actions for an already-selected unit
		if(token.CurrentUnit != null) {
			// Targeting
			if(token.CanAttack || token.CanHeal) {
				if(IntendedTarget != token) {
					if(CanTargetFromToken(token)) {
						SetIntendedTarget(token);
					}
				}else{
					ConfirmTargetAction(token.CurrentUnit);
				}
			// Selecting
			}
			else {
				if(SelectedToken != null) {
					if(token != SelectedToken) {
						SelectedToken.CurrentUnit.UnselectUnit();
					}
				}
				token.CurrentUnit.Clicked(token);
			}
		}
		// Moving
		else if(token.CanMove) {
			if(IntendedMove != token) {
				SetIntendedMove(token);
			}else {
				ConfirmMove();
			}
		}
		// Unselecting
		else {
			if(SelectedToken != null) {
				SelectedToken.CurrentUnit.UnselectUnit();
			}
		}
	}

	/**
	 * Runs when a unit is selected. Take action if possible, otherwise show unit info
	 * <param name="token">The token on which the unit to be selected is currently located</param>
	 */
	public void SelectUnit(Token token) {
		SelectedToken = token;
		Unit unit = token.CurrentUnit;

		if(unit != null) {
			ShowUnitInfo(unit);

			SelectedToken.CurrentUnit = unit;
			if(unit.MyTeam && !unit.Acted && GameData.CurrentMatch.UserTurn) {
				SetValidActions(token);
			}
		}
	}

	/**
	 * Runs when a unit is unselected (i.e. user clicks other unit, or unit takes turn)
	 */
	public void UnselectUnit() {
		_unitInfoController.RemoveUnitInfo();
		_selectedToken = null;
		IntendedMove = null;
		UnselectTarget();
		ClearArrows();
		ClearValidActions();
	}

	/**
	 * Activates the error message popup and sets its display text to the provided value
	 * <param name="errorText">The error message to be displayed</param>
	 */
	public static void DisplayGameErrorMessage(string errorText){
		Text[] errorChildren = GameController.ErrorMessagePopup.GetComponentsInChildren<Text>();
		errorChildren[GameController.ERR_TEXT_IDX].text = errorText;
		GameController.ErrorMessagePopup.gameObject.SetActive(true);
	}

	/**
	 * Takes a hex string and converts it to a color object
	 * <param name="hex">The hex string value to convert</param>
	 * <returns>A color object representing the provided color</returns>
	 */
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

// ---------------------------------------------------------------------------------------------------------------------
// Private Functions ---------------------------------------------------------------------------------------------------
	/**
	 * To check if all units are placed for a specified team
	 * <param name="alliedTeam">true for allied team, false for enemy</param>
	 * <returns>True if all units are placed for the specified team</returns>
	 */
	private static bool UnitsArePlaced(bool alliedTeam) {
		Dictionary<int, Unit> unitList = null;
 		if(alliedTeam){
			unitList = GameData.CurrentMatch.AlliedUnits;
		}
		else{
			unitList = GameData.CurrentMatch.EnemyUnits;
		}
		foreach(Unit unit in unitList.Values) {
			if(unit.X == -1) {
				return false;
			}
		}
		return true;
	}

	/**
	 * Run when turn someone ends their turn
	 */
	private static void ChangeTurn() {
		foreach(Unit unit in _units) {
			unit.Reset();
		}
	}

	/**
	 * Token actions when unit is placed
	 * <param name="token">The token on which to place the unit</param>
	 */
	private static void PlaceUnit(Token token) {
		Unit placedUnit = new Unit(UnitBeingPlaced.ID, UnitBeingPlaced.UnitName, token.X, token.Y);

		SC.SpawnUnit(placedUnit);
		token.CurrentUnit = placedUnit;
	}

	/**
	 * Shows information about an acting unit
	 * <param name="unit">The unit whose information is to be displated</param>
	 */
	private static void ShowUnitInfo(Unit unit) {
		_unitInfoController.SetUnitInfo(unit);
	}

	/**
	 * Shows information about a unit being targeted
	 * <param name="unit">The unit whose information is to be displated</param>
	 */
	private static void ShowTargetInfo(Unit unit) {
		_targetInfoController.SetUnitInfo(unit);
		TargetDetailsController.Main.SetDetails();
	}

	/**
	 * Repaints the available actions after a unit's intended move is set
	 */
	private void PaintIntendedMoveActions() {
		foreach(KeyValuePair<int, Dictionary<int, int>> key1 in _actions) {
			Dictionary<int, int> key2 = key1.Value;
			foreach(int y in key2.Keys){
				Token currToken = Tokens[key1.Key][y];
				if(currToken == IntendedMove || CanTargetFromToken(currToken)) {
					continue;
				}
				currToken.SetActionProperties("clear");
			}
		}
	}

	/**
	 * Checks whether the unit can target from IntendedMove
	 * <param name="currToken">The token targeted</param>
	 * <returns>True if the CurrentUnit can target the unit on that token</returns>
	 */
	private static bool CanTargetFromToken(Token currToken) {
		if((currToken.CanAttack && currToken.HasEnemy()) || (currToken.CanHeal && currToken.HasAlly())) {
			int _deltaX = (IntendedMove != null)? Mathf.Abs(IntendedMove.X - currToken.X) : Mathf.Abs(SelectedToken.X - currToken.X);
			int _deltaY = (IntendedMove != null)? Mathf.Abs(IntendedMove.Y - currToken.Y) : Mathf.Abs(SelectedToken.Y - currToken.Y);
			int range = GameData.GetUnit(SelectedToken.CurrentUnit.UnitName).GetStat("Attack Range").Value;
			return range >= _deltaX + _deltaY;
		}
		return false;
	}

	/**
	 * Move unit to new token and paint new actions
	 * <param name="token">The token on which to move the unit</param>
	 */
	private void SetIntendedMove(Token token) {
		UnselectTarget();
		ClearArrows();

		if(_selectedToken.X != token.X || _selectedToken.Y != token.Y){
			DrawMovementArrows(token);
		}

		IntendedMove = token;
		PaintIntendedMoveActions();
	}

	/**
	 * Determines the shortest valid path to the target token and draws an arrow to it
	 * Assumes the _selectedToken has been set as the moving unit
	 * <param name="token">The target token to which the unit is moving</param>
	 */
	private void DrawMovementArrows(Token token){
		// Name of moving unit is used in  weight determiniation
		string unitName = _selectedToken.CurrentUnit.UnitName;

		int[][] weightMap = JaggedArray.CreateJaggedArray<int[][]>(_gridLength, _gridHeight);
		int MAX_DIST = GameData.GetUnit(unitName).GetStat("Move").Value;
		for(int x = 0; x < _gridLength; x++){
			for(int y = 0; y < _gridHeight; y++){
				weightMap[x][y] = MAX_DIST;
			}
		}

		PriorityQueue<vertex> tokensToProcess = new PriorityQueue<vertex>();

		// Enqueue the starting node with 0 distance and maximum priority
		int MAX_PRIORITY = 999;
		tokensToProcess.Enqueue(MAX_PRIORITY, new vertex(_selectedToken.X, _selectedToken.Y, 0));
		weightMap[_selectedToken.X][_selectedToken.Y] = 0;

		// Declare loop variables once
		vertex v;
		int testX;
		int testY;
		int terrainWeight;
		int newDist;
		Token currToken = null;
		vertex foundTarget = null;

		// Loop until all valid tokens in range are checked or the target location is found
		while(tokensToProcess.Count > 0){
			v = tokensToProcess.Dequeue();

			// If this test X and Y are the coordinates we are looking for, we're done!
			if(v.x == token.X && v.y == token.Y){
				foundTarget = v;
				break;
			}

			// Loop over the token's cardinal direction neighbors
			foreach(Twople<int, int> nbr in GC_NEIGHBORS){
				testX = v.x + nbr.Item1;
				testY = v.y + nbr.Item2;

				// Skip checking if the location is not on the map
				if(testX >= _gridLength || testX < 0 || testY >= _gridHeight || testY < 0){
					continue;
				}

				// Skip checking if the token is attackable (can't move to or through it)
				currToken = _tokens[testX][testY];
				if(currToken.CurrentUnit != null && !currToken.CurrentUnit.MyTeam){
					continue;
				}

				// Next token's distance is current token's distance + terrain weight of next token
				terrainWeight = GameData.TerrainWeight(unitName, _tokens[testX][testY].CurrentTerrain.ShortName);
				newDist = v.dist + terrainWeight;
				if(newDist <= weightMap[testX][testY]){
					tokensToProcess.Enqueue(MAX_PRIORITY - newDist, new vertex(testX, testY, newDist, v));
				}

			}

			if(foundTarget != null){
				break;
			}
		}

		vertex f = foundTarget;
		bool endArrow = true;
	 	float dx;
		float dy;

		// Because (0, 0) is top left, not bottom left, the dy is negated
		dx = (float)f.x - (float)f.prev.x;
		dy = -((float)f.y - (float)f.prev.y);
		CreateArrow(f.x, f.y, _scale, _orthoSize, dx, dy, endArrow);
		endArrow = false;
		while(f.prev != null){
			dx = (float)f.x - (float)f.prev.x;
			dy = -((float)f.y - (float)f.prev.y);
			CreateArrow(f.x, f.y, _scale, _orthoSize, dx, dy, endArrow);
			f = f.prev;

		}

		// Arrow must also flip if the user is on the other team
		MovementArrows.transform.eulerAngles = new Vector3(0,0,(GameData.CurrentMatch.UserTeam == 1)? 180 : 0);
	}
	// Helper class (struct) for above function DrawMovementArrows()
	private class vertex{
		public int x;
		public int y;
		public int dist;
		public vertex prev;

		public vertex(int _x, int _y, int _dist, vertex _prev = null){
			x = _x;
			y = _y;
			dist = _dist;
			prev = _prev;
		}
	};

	/**
	 * Instantiates and properly positions either an arrow segment or the end of the arrow on the grid
	 * <param name="x">The x position of where the segement is placed</param>
	 * <param name="y">The y position of where the segement is placed</param>
	 * <param name="scale">The scale used in positioning the arrow</param>
	 * <param name="size">The size used in determining how big to make the arrow</param>
	 * <param name="dx">The x offset for where to point the arrow</param>
	 * <param name="dy">The y offset for where to point the arrow</param>
	 * <param name="endArrow">True only when painting the end of the arrow</param>
	 */
	private static void CreateArrow(int x, int y, float scale, float size, float dx, float dy, bool endArrow){
		// Determine position of the arrow segment: offset towards next token
		float xPos = (endArrow)? x * scale: ((float)x - (dx / 2)) * scale;
		float yPos = (endArrow)? y * scale: ((float)y + (dy / 2)) * scale;
		Vector3 position = new Vector2(xPos - size, -yPos + size) + new Vector2(scale / 2f, - scale / 2f);

		// Create the arrow segment
		string objectToLoad = (endArrow)? "Materials/Arrow": "Materials/MovementCylinder";
		UnityEngine.Object arrObj = Instantiate(Resources.Load(objectToLoad), position,
			Quaternion.identity, MovementArrows.transform);
		GameObject arrow = (arrObj as GameObject);

		// Determine the arrows rotation
		float rotation = ((float)Math.Atan2(dy, dx)) * (180 / (float)Math.PI);
		arrow.gameObject.transform.Rotate(0, 0, rotation);

		// Set the name to be its coordinates
		arrow.gameObject.name = ((endArrow)?"End: ": "Segment: ") + " (" + x + ", " + y + ")";
		arrow.gameObject.transform.localScale = new Vector3(scale, scale, 1);
	}

	/**
	 * Clears all of the arrow segments and head of the arrow
	 */
	private static void ClearArrows(){
		foreach (Transform child in MovementArrows.transform) {
			GameObject.Destroy(child.gameObject);
		}

		MovementArrows.transform.eulerAngles = new Vector3(0, 0, 0);
	}

	/**
	 * Confirm move unit to new token and unselect after
	 */
	private static void ConfirmMove() {
		Dictionary<string, object> response = Server.TakeNonTargetAction(SelectedToken.CurrentUnit,
			"Wait", IntendedMove.X, IntendedMove.Y);
		if(Parse.Bool(response["Success"])){
			MoveUnit();
		}
		else{
			GameController.DisplayGameErrorMessage(Parse.String(response["Error"]));
		}
	}

	/**
	 * All the actions when moving a unit
	 */
	private static void MoveUnit() {
		bool coordChanged = (IntendedMove.X != _selectedToken.X) || (IntendedMove.Y != _selectedToken.Y);
		IntendedMove.CurrentUnit = SelectedToken.CurrentUnit;
		if(coordChanged) {
			IntendedMove.CurrentUnit.transform.position = IntendedMove.gameObject.transform.position;
			_selectedToken.CurrentUnit = null;
		}
		IntendedMove.CurrentUnit.ConfirmMove();
	}

	/**
	 * When your unit is already selected and you choose a target
	 * <param name="token">The token being targeted</param>
	 */
	private void SetIntendedTarget(Token token) {
		if(IntendedMove == null) {
			// If targeting from current token, IntendedMove will be null so set it now
			SetIntendedMove(SelectedToken);
		}
		UnselectTarget();
		IntendedTarget = token;
		IntendedTarget.gameObject.GetComponent<SpriteRenderer>().color = HexToColor("000000FF");
		ShowTargetInfo(IntendedTarget.CurrentUnit);
	}

	/**
	 * Unselects the target token
	 */
	public void UnselectTarget() {
		if(IntendedTarget != null) {
			IntendedTarget.gameObject.GetComponent<SpriteRenderer>().color = HexToColor("FFFFFFFF");
			_targetInfoController.RemoveUnitInfo();
			IntendedTarget = null;
		}
	}

	/**
	 * Confirms attack target and moves to intended token if applicable
	 * <param name="targetUnit">The unit being targeted</param>
	 */
	private void ConfirmTargetAction(Unit targetUnit) {
		// Confirm whether the target token is red or green (attack or heal)
		string action = (IntendedTarget.CanAttack)? "Attack" : "Heal";

		// Take the targeted action
		Dictionary<string, object> response = Server.TakeTargetAction(SelectedToken.CurrentUnit, action,
			targetUnit.ID, IntendedMove.X, IntendedMove.Y);

		if(Parse.Bool(response["Success"])) {
			Dictionary<string, object> unitDict   = (Dictionary<string, object>)response["Unit"];
			Dictionary<string, object> targetDict = (Dictionary<string, object>)response["Target"];

			// Update unit info
			SelectedToken.CurrentUnit.UpdateInfo(Parse.Int(unitDict["NewHP"]));
			targetUnit.UpdateInfo(Parse.Int(targetDict["NewHP"]));
			if(SelectedToken.CurrentUnit.HP <= 0) {
				SelectedToken.CurrentUnit.Destroy();
				SelectedToken.CurrentUnit = null;
				UnselectUnit();
			}
			if(targetUnit.HP <= 0) {
				GameController.Tokens[targetUnit.X][targetUnit.Y].CurrentUnit = null;
				targetUnit.Destroy();
			}
			MoveUnit();
		}
		else{
			GameController.DisplayGameErrorMessage(Parse.String(response["Error"]));
		}
	}

	/**
	 * Assess valid moves for the selected unit. After all actions have been assessed, paint the tokens.
	 * <param name="token">The token selected which has a movable unit on it</param>
	 */
	private void SetValidActions(Token token) {
		// Reset valid actions and queue of remaining tokens to check
		ClearValidActions();

		// Info about the unit being checked
		Unit movingUnit = token.CurrentUnit;
		string unitName = movingUnit.UnitName;
		int movementRemaining = GameData.GetUnit(unitName).GetStat("Move").Value;

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
		int currX;
		int currY;
		int terrainWeight;
		bool checkNeighbors = false;

		// Determmine if the unit can attack or heal before entering loop
		bool canAttack = GameData.GetUnit(unitName).Can("Attack");
		bool canHeal = GameData.GetUnit(unitName).Can("Heal");

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

				if(currElement.Item2 >= 0){
					checkNeighbors = true;

					// During movement phase, can move onto self or unoccupied locations
					if(currElement.Item1.CurrentUnit == null ||
							currElement.Item1.CurrentUnit.ID == movingUnit.ID)
					{
						AddToActions(currX, currY, phase);
						currElement.Item1.SetActionProperties(((UnitAction)phase).ToString());
					}
					// Logic to handle a token with a unit:
					else if(currElement.Item1.CurrentUnit != null &&
							currElement.Item1.CurrentUnit.ID != movingUnit.ID)
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
									if(InMoveRangeToAct(currX, currY, currElement.Item2)){
										AddToActions(currX, currY, (int)UnitAction.heal);
										currElement.Item1.SetActionProperties("heal");
									}
									break;
							}
						}
						// Logic for when the token is occupied by an enemy
						else{
							// If still moving, add this to attack check for after movement is done
							switch(phase){
								case (int)UnitAction.move:
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
									break;
								case (int)UnitAction.attack:
									if(InMoveRangeToAct(currX, currY, currElement.Item2)){
										AddToActions(currX, currY, (int)UnitAction.attack);
										currElement.Item1.SetActionProperties("attack");
									}
									break;
							}
						}
					}

					// Add the 4 neighbors to the queue to be checked
					if(checkNeighbors){
						foreach(Twople<int, int> nbr in GC_NEIGHBORS){
							if(currX + nbr.Item1 < GridLength && currX + nbr.Item1 >= 0 &&
							   currY + nbr.Item2 < GridHeight && currY + nbr.Item2 >= 0) {
								if(!queuedTokens[currX + nbr.Item1][currY + nbr.Item2]){
									queuedTokens[currX + nbr.Item1][currY + nbr.Item2] = true;

									// Movement remaining is existing remaining movement - terrain weight
									terrainWeight = GameData.TerrainWeight(unitName, Tokens[currX + nbr.Item1][currY + nbr.Item2].CurrentTerrain.ShortName);
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

		foreach(KeyValuePair<int, Dictionary<int, int>> key1 in _actions) {
			foreach(KeyValuePair<int, int> key2 in key1.Value){
				Tokens[key1.Key][key2.Key].PaintAction(((UnitAction)key2.Value).ToString());
			}
		}
	}

	/**
	 * Clears the token vars and actions list
	 */
	private void ClearValidActions() {
		foreach(KeyValuePair<int, Dictionary<int, int>> key1 in _actions) {
			Dictionary<int, int> key2 = key1.Value;
			foreach(int y in key2.Keys){
				Tokens[key1.Key][y].SetActionProperties("clear");
			}
		}
		_actions = new Dictionary<int, Dictionary<int, int>>();
	}

	/**
	 * Initializes the game UI when opening after place units has already been completed
	 */
	private void InitializeUI() {
		GameController.ErrorMessagePopup = GameObject.Find("GameErrorMessage").GetComponent<RectTransform>();
		CloseErrorMessage();
		EndTurnGO.transform.Find("Confirm").gameObject.SetActive(false);
		BackToMenuGO.SetActive(false);
		_displayEndTurn = false;
		_displayBackToMenu = false;
		if(!GameData.CurrentMatch.UserTurn || PlacingUnits || !UnitsArePlaced(GC_ENEMY_TEAM)) {
			EndTurnGO.SetActive(false);
		}

		// Set scale factors
		_orthoSize = Camera.main.orthographicSize;
		_scale = (2f * _orthoSize) / (float)_tokens.Length;
	}

	/**
	 * Initializes the game map when opening after place units has already been completed
	 */
	private void InitializeMap() {
		foreach(Unit unit in GameData.CurrentMatch.AlliedUnits.Values) {
			SC.SpawnUnit(unit);
		}
		foreach(Unit unit in GameData.CurrentMatch.EnemyUnits.Values) {
			SC.SpawnUnit(unit);
		}
	}

	/**
	 * Adds an action to the list of available actions for a unit
	 * <param name="x">The X coordinate of the valid action</param>
	 * <param name="y">The Y coordinate of the valid action</param>
	 * <param name="actionType">The integer value representing the action that can be taken</param>
	 */
	private void AddToActions(int x, int y, int actionType){
		if(!_actions.ContainsKey(x)){
			_actions[x] = new Dictionary<int, int>();
		}
		_actions[x][y] = actionType;
	}

	/**
	 * Determines if the provided token is within a valid range of a movement square
	 * <param name="x">The X token being checked for the action</param>
	 * <param name="y">The Y token being checked for the action</param>
	 * <param name="rangeRemaining">A move token must be within this range</param>
	 */
	// TODO: Add to list of dictionaries with rangeRemaining sizes
	private bool InMoveRangeToAct(int x, int y, int rangeRemaining){
		int maxRangeAccepted = rangeRemaining + 1;

		// Get a list of all coordinates within rangeRemaining spaces of this token
		List<Twople<int, int>> actionRange = new List<Twople<int, int>>();
		for(int xRng = -maxRangeAccepted; xRng <= maxRangeAccepted; xRng++){
			// Ensure X is within the grid
			if(x + xRng >= _gridLength || x + xRng < 0){
				continue;
			}

			for(int yRng = -maxRangeAccepted; yRng <= maxRangeAccepted; yRng++){
				// Ensure the two numbers combied are within the range (check within diamond of unit, not square)
				if(Math.Abs(xRng) + Math.Abs(yRng) > maxRangeAccepted){
					continue;
				}

				// Ensure Y is within the grid
				if(y + yRng >= _gridHeight || y + yRng < 0){
					continue;
				}

				actionRange.Add(Twople.Create(xRng, yRng));
			}
		}

		// For each token within range of this token, if one is a move, can target here
		int testX;
		int testY;
		foreach(Twople<int, int> coord in actionRange){
			testX = x + coord.Item1;
			testY = y + coord.Item2;
			if(_actions.ContainsKey(testX) && _actions[testX].ContainsKey(testY)
					&& _actions[testX][testY] == (int)UnitAction.move){
				return true;
			}
		}

		return false;
	}

}

// Struct for unit's actions when clicked
public struct ValidAction {
	public string action;
	public int col;
	public int row;
}

enum UnitAction{ move = 0, attack = 1, heal = 2, none = 3 };
