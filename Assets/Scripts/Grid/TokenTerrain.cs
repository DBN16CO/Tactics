using UnityEngine;					// Because we reference GameObjects

// Class governing the various terrains of the game
public class TokenTerrain {

	private string _name;			// The name of the terrain


#region Setters and Getters
	// Returns _name
	public string Name {
		get{return _name;}
		set{_name = value;}
	}
#endregion


	// Sets sprite on input token's SpriteRenderer
	public void SetSprite(GameObject token) {
		// Get Sprite Renderer component and set equal to the sprite in the resources folder
		token.GetComponent<SpriteRenderer>().sprite = Resources.Load("Prefabs/Sprites/Terrain/" + Name) as Sprite;
	}

}