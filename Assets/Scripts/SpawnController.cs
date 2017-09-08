using UnityEngine;

public class SpawnController : ParentController {

	private float _scaleFactor;		// What to scale each 1x1 unit by to fit on the screen


#region Setters and Getters
	// Returns the scale factor for each sprite
	public float ScaleFactor {
		get{return _scaleFactor;}
		set{_scaleFactor = value;}
	}
#endregion

	// Call this to instantiate a new game grid
	public void CreateMap(string mapKey) {
		MapData map = GameData.GetMaps[mapKey];
		// Initialize Tokens jagged array
		Token[][] tokens = new Token[map.Width][];
		for(int x = 0; x < tokens.Length; x++) {
			tokens[x] = new Token[map.Height];
		}
		// Set scale factor based on orthographic camera settings
		// Assumes PPU = resolution for each sprite
		float orthoSize = Camera.main.orthographicSize;
		ScaleFactor = (2f * orthoSize) / (float)tokens.Length; 		// This will have to change if we want non-square maps
//		Camera.main.transform.eulerAngles = new Vector3(0,0,(GameData.CurrentMatch.UserTeam == 1)? 180 : 0);
		// Loop through each token
		GameObject GameMap = new GameObject(); GameMap.name = "MapTokens";
		for(int width = 0; width < tokens.Length; width++) {
			for(int height = 0; height < tokens[width].Length; height++) {
				// Instantiate token at each grid position
				Token token = (Instantiate(Resources.Load("Prefabs/Token"),new Vector2(((float)width*ScaleFactor)-orthoSize,-((float)height*ScaleFactor)+orthoSize) + new Vector2(ScaleFactor/2f,-ScaleFactor/2f),Quaternion.identity, GameMap.transform) as GameObject).GetComponent<Token>();
				// Set scale to scale factor
				token.gameObject.transform.localScale = new Vector3(ScaleFactor,ScaleFactor,1);
				// Assign terrain based on preset map
				string terr = map.Terrain[width][height];
				token.SetTerrain(terr);
				// Asign token variables
				token.X = width;
				token.Y = height;
				// If placing units, grey out the tokens that can't be placed on
				if(GameController.PlacingUnits && gameObject.GetComponent<GameController>().CurrentMap.TeamPlaceUnit[width][height] != gameObject.GetComponent<GameController>().myTeam) {
					token.SetActionProperties("disabled");
				}
				// Add token to token array
				tokens[width][height] = token;
			}
		}
		GameMap.transform.eulerAngles = new Vector3(0,0,(GameData.CurrentMatch.UserTeam == 1)? 180 : 0);
		// Set game vars
		GameController.GridLength = tokens.Length;
		GameController.GridHeight = tokens[0].Length;
		GameController.Tokens = tokens;
	}

	// Call this to create a unit for a token
	public Unit CreateUnit(UnitInfo unit,int x, int y, bool myTeam) {
		// Initialize return unit as null in case it's dead
		Unit ret = null;
		// Instantiate the specified unit if not dead
		if(unit.HP > 0 || GameController.PlacingUnits) {
			ret = (Instantiate(Resources.Load("Units/" + unit.Name),Vector3.zero,Quaternion.identity) as GameObject).GetComponent<Unit>();
			// Set the position to the token's position
			ret.transform.position = GameController.Tokens[x][y].transform.position;
			ret.gameObject.transform.localScale = new Vector3(ScaleFactor,ScaleFactor,1);
			// Add to GameController Units and Return final unit
			if(unit.X == -1 || unit.Y == -1) {
				// Set initial params if new unit
				unit.UpdateInfo(GameData.GetUnits[unit.Name].GetStats["HP"].Value, x, y);
			}
			ret.Info = unit;
			ret.MyTeam = myTeam;

			// If the unit is on the opposite team of the user who's turn it is
			if((GameData.CurrentMatch.UserTurn && !ret.MyTeam) || (!GameData.CurrentMatch.UserTurn && ret.MyTeam)) {
				// Disabled doesn't apply if it's not the user's turn
				ret.PaintUnit((ret.MyTeam)? "ally" : "enemy");
			}
			// If the unit is on the same team of the user who's turn it is
			else {
				// Disabled does apply if it's the user's turn
				ret.PaintUnit((ret.Info.Acted)? "disable" : (ret.MyTeam)? "ally" : "enemy");
			}

			GameController.Tokens[x][y].CurrentUnit = ret;
			GameController.Units.Add(ret);

			if(myTeam){
				GameController.Main.myUnits[unit.ID] = ret;
			}
			else{
				GameController.Main.enemyUnits[unit.ID] = ret;
			}

			if(GameController.PlacingUnits) {
				GameController.UnitBeingPlaced.RemoveUnit();
			}
		}
		return ret;
	}

	public static void ReturnPlacedUnit(Unit unit) {
		GameController.PU.AddUnit(unit.Info);
		DestroyUnit(unit);
	}

	public static void DestroyUnit(Unit unit) {
		GameController.Units.Remove(unit);
		Destroy(unit.gameObject);
	}

}

