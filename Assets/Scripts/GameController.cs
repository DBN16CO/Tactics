using UnityEngine;

public class GameController : MonoBehaviour {

	void Start() {
		Grid grid = gameObject.AddComponent<Grid>();
		grid.CreateGrid(10);
	}

}
