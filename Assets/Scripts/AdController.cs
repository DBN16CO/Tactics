using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class AdController : MonoBehaviour {

	public Button btn;

	// Use this for initialization
	void Start () {
		btn = gameObject.GetComponent<Button>();
		btn.onClick.AddListener(TaskOnClick);
	}

	// Runs when the app is closed - attempt to close the websocket cleanly
	void OnApplicationQuit() {
		CommunicationManager.OnDisable();
	}

	void TaskOnClick(){
		//Application.OpenURL("https://pbs.twimg.com/profile_images/2932495059/f664298aa5c7554496fc503909b94466_400x400.jpeg");
		if(Server.Logout()) {
			SceneManager.LoadSceneAsync("Startup", LoadSceneMode.Single);
		}
	}
}
