using UnityEngine;
using System.Collections.Generic;

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
	public Token[][] CreateGrid(int size) {
		// Initialize Tokens jagged array
		Token[][] tokens = new Token[size][];
		for(int x = 0; x < size; x++) {
			tokens[x] = new Token[size];
		}
		// Set scale factor based on orthographic camera settings
		// Assumes PPU = resolution for each sprite
		float orthoSize = Camera.main.orthographicSize;
		ScaleFactor = (2f * orthoSize) / (float)size;
		// Loop through each token
		for(int width = 0; width < size; width++) {
			for(int height = 0; height < size; height++) {
				// Instantiate token at each grid position
				Token token = (Instantiate(Resources.Load("Prefabs/Token"),new Vector2(((float)width*ScaleFactor)-orthoSize,((float)height*ScaleFactor)-orthoSize) + new Vector2(ScaleFactor/2f,ScaleFactor/2f),Quaternion.identity) as GameObject).GetComponent<Token>();
				// Set scale to scale factor
				token.gameObject.transform.localScale = new Vector3(ScaleFactor,ScaleFactor,1);
				// Assign terrain based on preset map
				// For development, set to w/e we want
				string terr = (Random.value > 0.3f)? "Grass" : "Forest";
				token.SetTerrain(terr);
				// Asign token variables
				token.X = width;
				token.Y = height;
				// Add token to token array
				tokens[width][height] = token;
			}
		}
		// Set game vars and return token array
		gameObject.GetComponent<GameController>().GridLength = tokens.Length - 1;
		gameObject.GetComponent<GameController>().GridHeight = tokens[0].Length - 1;
		return tokens;
	}

	// Call this to create a unit for a token
	public Unit CreateUnit(string unit,int x, int y) {
		// Instantiate the specified unit
		Unit ret = (Instantiate(Resources.Load("Prefabs/" + unit),Vector3.zero,Quaternion.identity) as GameObject).GetComponent<Unit>();
		// Set the position to the token's position
		ret.transform.position = gameObject.GetComponent<GameController>().Tokens[x][y].transform.position;
		ret.gameObject.transform.localScale = new Vector3(ScaleFactor,ScaleFactor,1);
		// Remove (clone) from the name
		ret.name = ret.name.Substring(0, ret.name.Length-7);
		// Return final unit
		return ret;
	}

}

