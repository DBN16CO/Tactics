using UnityEngine;

public class Grid : MonoBehaviour{

	private Token[][] _tokens;


#region Setters and Getters
	// Returns _tokens
	public Token[][] Tokens {
		get{return _tokens;}
		set{_tokens = value;}
	}
#endregion


	// Runs when a new grid is instantiated
	public void CreateGrid(int size) {
		// Create Tokens jagged array
		Tokens = new Token[size][];
		for(int x = 0; x < size; x++) {
			Tokens[x] = new Token[size];
		}

		float orthoSize = Camera.main.orthographicSize;
		float tokenScale = (2f * orthoSize) / (float)size;
		for(int width = 0; width < size; width++) {
			for(int height = 0; height < size; height++) {
				Token token = (Instantiate(Resources.Load("Prefabs/Token"),new Vector2(((float)width*tokenScale)-orthoSize,((float)height*tokenScale)-orthoSize),Quaternion.identity) as GameObject).GetComponent<Token>();
				token.gameObject.transform.localScale = new Vector3(tokenScale,tokenScale,1);
				token.SetTerrain("Grass");
				Tokens[width][height] = token;
				token.X = width;
				token.Y = height;
			}
		}
	}

}
