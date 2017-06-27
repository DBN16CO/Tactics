using UnityEngine;

public class SpawnController : MonoBehaviour {

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
		MapData map = GameData.GetMap(mapKey);
		// Initialize Tokens jagged array
		Token[][] tokens = new Token[map.width][];
		for(int x = 0; x < tokens.Length; x++) {
			tokens[x] = new Token[map.height];
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
				string terr = map.terrain[width][height];
				token.SetTerrain(terr);
				// Asign token variables
				token.X = width;
				token.Y = height;
				// If placing units, grey out the tokens that can't be placed on
				if(GameController.PlacingUnits && gameObject.GetComponent<GameController>().CurrentMap.teamPlaceUnit[width][height] != gameObject.GetComponent<GameController>().myTeam) {
					token.SetActionProperties("disabled");
				}
				// Add token to token array
				tokens[width][height] = token;
			}
		}
		GameMap.transform.eulerAngles = new Vector3(0,0,(GameData.CurrentMatch.UserTeam == 1)? 180 : 0);
		// Set game vars
		GameController.GridLength = tokens.Length - 1;
		GameController.GridHeight = tokens[0].Length - 1;
		GameController.Tokens = tokens;
	}

	// Call this to create a unit for a token
	public Unit CreateUnit(MatchUnit unit,int x, int y, bool myTeam) {
		// Instantiate the specified unit
		Unit ret = (Instantiate(Resources.Load("Units/" + unit.Name),Vector3.zero,Quaternion.identity) as GameObject).GetComponent<Unit>();
		// Set the position to the token's position
		ret.transform.position = GameController.Tokens[x][y].transform.position;
		ret.gameObject.transform.localScale = new Vector3(ScaleFactor,ScaleFactor,1);
		// Add to GameController Units and Return final unit
		if(unit.X == -1 || unit.Y == -1) {
			// Set initial params if new unit
			unit.X = x; unit.Y = y; unit.HP = GameData.GetUnit(unit.Name).GetStat("HP").Value;
		}
		ret.Info = unit;
		ret.TakenAction = unit.Acted;
		ret.MyTeam = myTeam;
		ret.PaintUnit((ret.MyTeam)? ((ret.TakenAction)? "disable" : "move") : "enemy");
		GameController.Tokens[x][y].CurrentUnit = ret;
		GameController.Units.Add(ret);
		if(GameController.PlacingUnits) {
			GameController.UnitBeingPlaced.RemoveUnit();
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

