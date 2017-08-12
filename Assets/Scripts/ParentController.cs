using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class ParentController : MonoBehaviour {

	// Runs when the app is closed - attempt to close the websocket cleanly
	void OnApplicationQuit() {
		CommunicationManager.OnDisable();
	}
}
