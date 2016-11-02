using UnityEngine;

public class GameController : MonoBehaviour {

	private Token[][] _tokens;


#region Setters and Getters
	// Returns _tokens
	public Token[][] Tokens {
		get{return _tokens;}
		set{_tokens = value;}
	}
#endregion


	void Start() {
		// Testing
		Test();
	}

	// For testing
	private void Test() {
		SpawnController SC = gameObject.AddComponent<SpawnController>();
		Tokens = SC.CreateGrid(8);
		Tokens[2][3].CurrentUnit = SC.CreateUnit("Warrior",2,3);
	}

	void Update() {
		// Testing move/zoom
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
		if(Input.GetKey("o")){
			Camera.main.orthographicSize /= 0.95f;
		}
	}

}
