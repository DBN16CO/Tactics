using UnityEngine;

public class SpawnController : ParentController {

	private float _scaleFactor;		// What to scale each 1x1 unit by to fit on the screen

	// Call this to instantiate a new game grid
	public void CreateMap(string mapKey) {
		MapData map = GameData.GetMap(mapKey);
		// Initialize Tokens jagged array
		Token[][] tokens = new Token[map.Width][];
		for(int x = 0; x < tokens.Length; x++) {
			tokens[x] = new Token[map.Height];
		}

		// Set scale factor based on orthographic camera settings, assumes PPU = resolution for each sprite
		float orthoSize = Camera.main.orthographicSize;
		_scaleFactor = (2f * orthoSize) / (float)tokens.Length;

		int myTeam = gameObject.GetComponent<GameController>().myTeam;
		MapData currentMap = gameObject.GetComponent<GameController>().CurrentMap;

		// Loop through each token
		for(int x = 0; x < tokens.Length; x++) {
			for(int y = 0; y < tokens[x].Length; y++) {
				// Assign terrain based on preset map
				string terr = map.Terrain[x][y];

				Token token = Token.Create(x, y, terr, _scaleFactor, orthoSize);

				// If placing units, grey out the tokens that can't be placed on
				if(GameController.PlacingUnits && currentMap.TeamPlaceUnit[x][y] != myTeam) {
					token.SetActionProperties("disabled");
				}

				// Add token to token array
				tokens[x][y] = token;
			}
		}

		// Flip the map if this user is not user 1
		GameController.MapTokens.transform.eulerAngles = new Vector3(0,0,(GameData.CurrentMatch.UserTeam == 1)? 180 : 0);

		// Set game vars
		GameController.GridLength = tokens.Length;
		GameController.GridHeight = tokens[0].Length;
		GameController.Tokens = tokens;
	}

	// Call this to create a unit object on a token
	public void SpawnUnit(Unit unit) {
		if(unit.HP <= 0 && ! GameController.PlacingUnits){
			return;
		}

		unit.Spawn(_scaleFactor);

		// Paint the unit appropriately
		string paintColor = (unit.MyTeam)? "ally" : "enemy";
		// If it is the owner of the unit's turn
		if((GameData.CurrentMatch.UserTurn && unit.MyTeam) || (!GameData.CurrentMatch.UserTurn && !unit.MyTeam)) {
			// Disabled applies if it's the user's turn
			if(unit.Acted){
				paintColor = "disable";
			}
		}
		unit.PaintUnit(paintColor);

		// Add the unit to the appropriate GameObject lists
		GameController.Tokens[unit.X][unit.Y].CurrentUnit = unit;
		GameController.Units.Add(unit);
		if(unit.MyTeam){
			GameController.AlliedUnits[unit.ID] = unit;
		}
		else{
			GameController.EnemyUnits[unit.ID] = unit;
		}

		// Remove unit from place units list
		if(GameController.PlacingUnits){
			GameController.UnitBeingPlaced.RemoveUnit();
		}
	}

	// Returns the placed unit back into the list of placable units
	public static void ReturnPlacedUnit(Unit unit) {
		GameController.Tokens[unit.X][unit.Y].CurrentUnit = null;
		GameController.PU.AddUnit(unit);
		DestroyUnit(unit);
	}

	// Destroys the Unit's GameObject
	public static void DestroyUnit(Unit unit) {
		GameController.Units.Remove(unit);
		unit.Destroy();
	}

}
