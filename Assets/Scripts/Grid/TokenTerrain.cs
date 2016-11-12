using UnityEngine;					// Because we reference GameObjects

// Class governing the various terrains of the game
public class TokenTerrain {

	private string _spriteName;			// The name of the terrain
	private int _moveWeight;


#region Setters and Getters
	// Returns _name
	public string SpriteName {
		get{return _spriteName;}
		set{_spriteName = value;}
	}
	// Returns _moveWeight
	public int MoveWeight {
		get{return _moveWeight;}
		set{_moveWeight = value;}
	}
#endregion


	// Sets sprite on input token's SpriteRenderer
	public void SetSprite(GameObject token) {
		// Get Sprite Renderer component and set equal to the sprite in the resources folder
		token.GetComponent<SpriteRenderer>().sprite = Resources.Load<Sprite>("Sprites/Terrain/" + SpriteName);
	}

}
