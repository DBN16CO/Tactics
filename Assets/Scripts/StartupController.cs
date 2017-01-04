using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class StartupController : MonoBehaviour {

	private string selectedButton;
	private bool _expanding;
	private bool _collapsing;
	private float _t;

	private RectTransform _panelRT;
	private RectTransform _emailRT;
	private RectTransform _passwordRT;
	private RectTransform _confirmPasswordRT;

	// Runs on app startup - start server connection, login, load game data
	void Start () {
		Server.Connect();

		PlayerPrefs.DeleteKey("session"); // Uncomment this to test from login screen

		if(PlayerPrefs.HasKey("session")) {
			if(!Server.RetryLogin()) {
				// Session token doesn't exist in database
				PlayerPrefs.DeleteKey("session");
				ShowLoginUI();
			}else{
				GoToMain();
			}
		}else{
			ShowLoginUI();
		}
	}

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

	private void ShowLoginUI() {
		selectedButton = "Login";
		_expanding = false;
		_collapsing = false;
		_t = 0f;

		_panelRT = (RectTransform)GameObject.Find("Panel").transform;
		_emailRT = (RectTransform)GameObject.Find("Email").transform;
		_passwordRT = (RectTransform)GameObject.Find("Password").transform;
		_confirmPasswordRT =(RectTransform)GameObject.Find("ConfirmPassword").transform;
	}

	public void Login() {
		string username = GameObject.Find("Username").GetComponent<InputField>().text;
		string password = GameObject.Find("Password").GetComponent<InputField>().text;

		if(selectedButton == "Login") {
			if(Server.Login(username, password)) {
				GoToMain();
			}
		}else{
			string email = GameObject.Find("Email").GetComponent<InputField>().text;
			string confirmpw = GameObject.Find("ConfirmPassword").GetComponent<InputField>().text;
			if(string.Equals(password, confirmpw)) {
				if(Server.CreateUser(username, password, email)) {
					if(Server.Login(username, password)) {
						GoToMain();
					}
				}
			}
		}
	}

	private void GoToMain() {
		Server.GetUserInfo();
		if(Server.InitialLoad()) {
			Screen.orientation = ScreenOrientation.LandscapeLeft;
			SceneManager.LoadSceneAsync("Game", LoadSceneMode.Single);
		}
	}

	// For dev - to quickly bypass
	private void TestLogin() {
		if(!Server.Login("testUser", "tactics")) {
			Server.CreateUser("testUser", "tactics", "tactics@gmail.com");
			Server.Login("testUser", "tactics");
		}
	}

}
