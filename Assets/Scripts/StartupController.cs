using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class StartupController : MonoBehaviour {

	private string selectedButton;		// Is login or register selected
	private bool _expanding;			// When register is clicked
	private bool _collapsing;			// When login is clicked
	private float _t;					// Arbitrary measure of time

	// References to the transforms of the moving objects
	private RectTransform _panelRT;
	private RectTransform _emailRT;
	private RectTransform _passwordRT;
	private RectTransform _confirmPasswordRT;


	// Runs on app startup - start server connection, login, load game data
	void Start () {
		
		CommunicationManager.Start();

		//PlayerPrefs.DeleteKey("session"); // Uncomment this to test from login screen
		
		// If session token works, go to game, otherwise remove token and init login UI
		if(PlayerPrefs.HasKey("session")) {
			if(!CommunicationManager.RetryLogin()) {
				PlayerPrefs.DeleteKey("session");
				Debug.Log("Initializing Login UI");
				InitLoginUI();
			}else{
				GoToMain();
			}
		}else{
			Debug.Log("Initializing Login UI");
			InitLoginUI();
		}
	}

	// Runs when the app is closed - attempt to close the websocket cleanly
	void OnApplicationQuit() {
		CommunicationManager.OnDisable();
	}

	// Runs every frame, lerps objects if _expanding or _collapsing
	void Update() {
		if(_t >= 1f) {
			_expanding = false;
			_collapsing = false;
			_t = 0f;
		}else if(_expanding) {
			_t += Time.deltaTime;
			_panelRT.sizeDelta = new Vector2(150f,Mathf.Lerp(_panelRT.sizeDelta.y,260f,_t));
			_emailRT.anchoredPosition = new Vector3(0,Mathf.Lerp(_emailRT.anchoredPosition.y,-148.75f,_t));
			_passwordRT.anchoredPosition = new Vector3(0,Mathf.Lerp(_passwordRT.anchoredPosition.y,-178.75f,_t));
			_confirmPasswordRT.anchoredPosition = new Vector3(0,Mathf.Lerp(_confirmPasswordRT.anchoredPosition.y,-208.75f,_t));
		}else if(_collapsing) {
			_t += Time.deltaTime;
			_panelRT.sizeDelta = new Vector2(150f,Mathf.Lerp(_panelRT.sizeDelta.y,200f,_t));
			_emailRT.anchoredPosition = new Vector3(0,Mathf.Lerp(_emailRT.anchoredPosition.y,-118.75f,_t));
			_passwordRT.anchoredPosition = new Vector3(0,Mathf.Lerp(_passwordRT.anchoredPosition.y,-148.75f,_t));
			_confirmPasswordRT.anchoredPosition = new Vector3(0,Mathf.Lerp(_confirmPasswordRT.anchoredPosition.y,-148.75f,_t));
		}
	}

	// Sets vars when login or register is clicked. Public so that it can be called from the scene
	public void ToggleLoginRegister(string buttonText) {
		if(selectedButton == "Login" && buttonText == "Register") {
			selectedButton = "Register";
			_t = 0f;
			_collapsing = false;
			_expanding = true;
		}else if(selectedButton == "Register" && buttonText == "Login") {
			selectedButton = "Login";
			_t = 0f;
			_expanding = false;
			_collapsing = true;
		}
	}

	// Inits vars for login UI
	private void InitLoginUI() {
		selectedButton = "Login";
		_expanding = false;
		_collapsing = false;
		_t = 0f;

		_panelRT = (RectTransform)GameObject.Find("Panel").transform;
		_emailRT = (RectTransform)GameObject.Find("Email").transform;
		_passwordRT = (RectTransform)GameObject.Find("Password").transform;
		_confirmPasswordRT =(RectTransform)GameObject.Find("ConfirmPassword").transform;
	}

	// Attempt to register or login. If successful, go to game. Public so can be called from scene
	public void Login() {
		string username = GameObject.Find("Username").GetComponent<InputField>().text;
		string password = GameObject.Find("Password").GetComponent<InputField>().text;

		if(selectedButton == "Register") {
			string email = GameObject.Find("Email").GetComponent<InputField>().text;
			string confirmpw = GameObject.Find("ConfirmPassword").GetComponent<InputField>().text;
			if(string.Equals(password, confirmpw)) {
				if(!Server.CreateUser(username, password, email)) {
					return;
				}
			}else{
				return;
			}
		}
		if(Server.Login(username, password)) {
			GoToMain();
		}
	}

	// Load game scene
	private void GoToMain() {
		Server.GetUserInfo();
		if(Server.InitialLoad()) {
			SceneManager.LoadSceneAsync("MainMenu", LoadSceneMode.Single);
		}
	}

}
