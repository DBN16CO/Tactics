using Common.Cryptography;			// For AES encryption
using System.Collections.Generic;	// Dictionary
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

using System.Threading;

public class StartupController : ParentController {

	private string selectedButton;		// Is login or register selected
	private bool _expanding;			// When register is clicked
	private bool _collapsing;			// When login is clicked
	private float _t;					// Arbitrary measure of time

	// References to the transforms of the moving objects
	private RectTransform _panelRT;
	private RectTransform _emailRT;
	private RectTransform _passwordRT;
	private RectTransform _confirmPasswordRT;
	private InputField _usernameText;
	private InputField _passwordText;
	private InputField _confirmPasswordText;
	private InputField _emailText;
	private Text _errorText;

	private bool _qguDone = false;
	private bool _guiDone = false;
	private bool _ilDone  = false;
	private Dictionary<string, object> _ilResponse = null;

	void Awake() {
		// Populate dictionary of called sever functions
		_functionMapping[RequestType.CU]  = HandleLgnResponse;	// Same response as logging in
		_functionMapping[RequestType.LGN] = HandleLgnResponse;
		_functionMapping[RequestType.GUI] = HandleGuiResponse;
		_functionMapping[RequestType.QGU] = HandleQguResponse;
		_functionMapping[RequestType.IL]  = HandleIlResponse;
	}


	// Runs on app startup - start server connection, login, load game data
	void Start () {
		//PlayerPrefs.DeleteKey("session"); // Uncomment this to test from login screen
		CommunicationManager.Start();

		Debug.Log("Initializing Login UI");
		InitLoginUI();

		// If session token works, go to game, otherwise remove token and init login UI
		if(PlayerPrefs.HasKey("session")) {
			Debug.Log("Logging in using token.");
			LoadingCircle.Show();
			Server.TokenLogin(this);
		}
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

		ProcessResponses();
		if(_ilResponse != null && _guiDone){
			GameData.SetGameData(_ilResponse);
			_ilDone = true;
		}
		if(_ilDone && _qguDone && _guiDone){
			LoadingCircle.Hide();
			SceneManager.LoadSceneAsync("MainMenu", LoadSceneMode.Single);
		}
	}

	// Sets vars when login or register is clicked. Public so that it can be called from the scene
	public void ToggleLoginRegister(string buttonText) {
		_errorText.text = "";

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
		_usernameText = GameObject.Find("Username").GetComponent<InputField>();
		_passwordText = GameObject.Find("Password").GetComponent<InputField>();
		_confirmPasswordText = GameObject.Find("ConfirmPassword").GetComponent<InputField>();
		_emailText = GameObject.Find("Email").GetComponent<InputField>();
		_errorText = GameObject.Find("LoginErrorText").GetComponent<UnityEngine.UI.Text>();
	}

	// Attempt to register or login. If successful, go to game. Public so can be called from scene
	public void Login() {
		_errorText.text = "";

		string username = _usernameText.text;
		string password = _passwordText.text;

		// If the user is registering
		if(selectedButton == "Register") {
			string email = _emailText.text;
			string confirmpw = _confirmPasswordText.text;

			// Ensure the password and confirm password match
			if(!string.Equals(password, confirmpw)) {
				_errorText.text = "The password fields do not match.";
				_passwordText.text = "";
				_confirmPasswordText.text = "";
				return;
			}

			Server.CreateUser(username, password, email, this);
		}
		// If the user is logging into Tactics
		else{
			Server.Login(username, password, this);
		}

		LoadingCircle.Show();
	}

	// Load game scene
	private void GoToMain(){
		Server.GetUserInfo(this);
		Server.QueryGames(this);
		Server.InitialLoad(this);
	}

	// Handles the Get User Info response
	private void HandleGuiResponse(Dictionary<string, object> response){
		GameData.SetPlayerData(response);
		_guiDone = true;
	}

	// Sets the _ilResponse dictionary so that static unit data can be loaded on the next frame.
	// This data depends on GUI to be loaded first.
	private void HandleIlResponse(Dictionary<string, object> response){
		_ilResponse = response;
	}

	// Handles the Query Games for User response
	private void HandleQguResponse(Dictionary<string, object> response){
		GameData.SetMatchData(response);
		GameData.SetMatchQueueData(response);
		_qguDone = true;
	}

	// Handles the Login or Create User responses, if successful, calls GUI, QGU, and IL
	private void HandleLgnResponse(Dictionary<string, object> response){
		if(!(bool)response["Success"]){
			Debug.Log("Login Error: " + Parse.String(response["Error"]));
			LoadingCircle.Hide();
			_passwordText.text = "";
			_confirmPasswordText.text = "";
			_errorText.text = Parse.String(response["Error"]);

			return;
		}

		string _loginToken = response["Token"].ToString();
		string _encryptedToken = AES.Encrypt(_loginToken, CommunicationManager.GenerateAESKey());
		PlayerPrefs.SetString("session", _encryptedToken);
		PlayerPrefs.Save();

		GoToMain();
	}

}
