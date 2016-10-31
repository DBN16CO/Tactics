using UnityEngine;					// Because we reference GameObjects

// Class governing the grass terrain type
public class Grass : TokenTerrain {

	// Runs when this terrain type is instantiated
	// Pass in token so we can set the sprite image
	public Grass(GameObject token) {
		// Name is used to generate asset path so make sure it is the sprite name in the resources folder
		string spriteName = "Grass33";
		Name = token.name = spriteName;
		// Calls parent function to set token's sprite image
		SetSprite(token);
	}

}