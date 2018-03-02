using System.Collections;			// IEnumerator
using System.Collections.Generic;	// Dictionary
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class AdController : ParentController {

	public Button btn;

	// Register server handlers
	void Awake(){
		_functionMapping[RequestType.LGO] = HandleLgoResponse;
	}

	// Use this for initialization
	void Start () {
		btn = gameObject.GetComponent<Button>();
		btn.onClick.AddListener(TaskOnClick);
	}

	void Update(){
		ProcessResponses();
	}

	void TaskOnClick(){
		//Application.OpenURL("https://pbs.twimg.com/profile_images/2932495059/f664298aa5c7554496fc503909b94466_400x400.jpeg");
		Server.Logout(this);
	}

	private IEnumerator HandleLgoResponse(Dictionary<string, object> response){
		// Delete player preferences regardless of request success
		PlayerPrefs.DeleteKey("session");
		PlayerPrefs.Save();
		SceneManager.LoadSceneAsync("Startup", LoadSceneMode.Single);

		yield return null;
	}
}
