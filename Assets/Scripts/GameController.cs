using UnityEngine;

public class GameController : MonoBehaviour {

	void Start() {
		Token token = (Instantiate(Resources.Load("Prefabs/Token"),new Vector3(0,0,0),Quaternion.identity) as GameObject).GetComponent<Token>();
		token.SetTerrain("Grass");
	}

}
