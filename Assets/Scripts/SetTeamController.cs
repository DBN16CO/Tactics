using System;					// DateTime
using System.Collections;		// IEnumerator
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

// This class controls the SetTeamController GameObject in the SetTeam scene
public class SetTeamController : ParentController {

	/* Constant vars */
	private static readonly DateTime STC_EPOCH = new DateTime(1970, 1, 1);
	public GameObject leader;					// The leader selected
	public string ability;						// The ability associated with that leader
	public List<string> units;					// A list of units, the element is the name of the unit
	public List<GameObject> perks;				// A list of perks, the index is the perk tier

	private int _fundsRemaining;				// The amount of $$$ left to spend
	private int _maxFunds;						// The total $$$ to spend

	/* Dynamic vars */
	public static Text ErrorMessageText;		// Text to be set on screen when an error is encountered

	/* Getters/Setters */
	// Either sets the text value on the screen or gets the int remaining funds
	public int FundsRemaining {
		get{return _fundsRemaining;}
		set{_fundsRemaining = value;
			GameObject.Find("Funds").transform.Find("Amount").GetComponent<Text>().text = "$" + _fundsRemaining + " / " + _maxFunds;}
	}

/// -----------------------------------------------------------------------------------------------
/// Unity methods ---------------------------------------------------------------------------------
	void Awake(){
		// Populate dictionary of called sever functions
		_functionMapping[RequestType.ST] = HandleStResponse;
		_functionMapping[RequestType.FM] = HandleFmResponse;
	}

	void Start () {
		// Populate LeaderTab
		List<string> strLeaders = new List<string>(GameData.Leaders.Keys);
		for(int i = 0; i < strLeaders.Count; i++) {
			AddLeader(i, GameData.GetLeader(strLeaders[i]));
		}
		// Populate UnitTab
		List<string> strUnits = new List<string>(GameData.Units.Keys);
		for(int i = 0; i < strUnits.Count; i++) {
			AddUnit(i, GameData.GetUnit(strUnits[i]));
		}
		// Populate PerkTab
		List<string> strPerks = new List<string>(GameData.Perks.Keys);
		for(int i = 0; i < strPerks.Count; i++) {
			AddPerk(i, GameData.GetPerk(strPerks[i]));
		}

		// Init variables
		leader = null;
		units = new List<string>();
		perks = new List<GameObject>(3) {null,null,null};
		_maxFunds = GameData.Version.MaxFunds;
		FundsRemaining = _maxFunds;
		ErrorMessageText = GameObject.Find("SetTeamErrorMessage").GetComponent<Text>();
	}

	void Update(){
		ProcessResponses();
	}

/// -----------------------------------------------------------------------------------------------
/// Public methods --------------------------------------------------------------------------------
	// Passes selected team to the database
	public void SetTeam() {
		ErrorMessageText.text = "";

		// Testing ------------
		if(leader != null) {
			LeaderData data = leader.GetComponent<SelectLeaderController>().data;
			List<string> strAbilities = new List<string>(data.Abilities.Keys);
			ability = data.Abilities[strAbilities[0]].Name;
		}else{
			ErrorMessageText.text = "Select a leader.";
			return;
		}
		// End Testing --------

		if(IsValidTeam()) {
			string strLeader = leader.name;
			List<string> strPerks = new List<string>();
			foreach(GameObject obj in perks) {
				if(obj != null) {
					strPerks.Add(obj.name);
				}
			}

			LoadingCircle.Show();
			Server.SetTeam(strLeader, ability, units, strPerks, this);
		}
		else{
			Debug.Log("Invalid team");
		}
	}

	// Returns the user to the main menu
	public void BackToMainMenu(){
		ErrorMessageText.text = "";
		SceneManager.LoadSceneAsync("MainMenu", LoadSceneMode.Single);
	}

/// -----------------------------------------------------------------------------------------------
/// Private methods -------------------------------------------------------------------------------
	// Returns whether selected team is valid or not
	private bool IsValidTeam() {
		// Ensure a leader has been selected
		if(leader == null){
			ErrorMessageText.text = "Please select a leader.";
			return false;
		}
		if(ability == null){
			ErrorMessageText.text = "Please select your leader's associated ability.";
			return false;
		}

		// Ensure the units selected are valid
		int minUnits = GameData.Version.MinUnits;
		if(units.Count < minUnits){
			ErrorMessageText.text = "You must select at least " + minUnits + " unit.";
			return false;
		}
		int maxUnits = GameData.Version.MaxUnits;
		if(units.Count > maxUnits){
			ErrorMessageText.text = "You cannot select more than " + maxUnits + " units.";
			return false;
		}

		// Ensure the user did not pick a team full of healers!
		bool noAttackerInTeam = true;
		for(int i = 0; i < units.Count; i++){
			if(string.Compare(units[i], "Cleric") != 0){
				noAttackerInTeam = false;
				break;
			}
		}
		if(noAttackerInTeam){
			ErrorMessageText.text = "Your team must have at least 1 unit that can attack.";
			return false;
		}

		// Ensure at least one perk has been selected
		bool noPerkSelected = true;
		for(int i = 0; i < perks.Count; i++){
			if(perks[i] != null){
				noPerkSelected = false;
				break;
			}
		}
		if(noPerkSelected){
			ErrorMessageText.text = "Please select at least 1 perk.";
			return false;
		}

		return true;
	}

	// Adds a leader to the screen
	private void AddLeader(int i, LeaderData leaderData) {
		// Instantiate GameObject, reposition based on index, assign specific game data, and resize scrollable area
		GameObject _leader = Instantiate(Resources.Load("Prefabs/TeamSelect/Leader"), Vector3.zero, Quaternion.identity, GameObject.Find("LeaderTabContent").transform) as GameObject;
		RectTransform _rt = _leader.GetComponent<RectTransform>();
		_rt.anchoredPosition = new Vector3((i % 3) * _rt.sizeDelta.x * _rt.localScale.x, (-i / 3) * _rt.sizeDelta.y * _rt.localScale.y);
		_leader.GetComponent<SelectLeaderController>().AssignLeader(leaderData);
		GameObject.Find("LeaderTabContent").GetComponent<RectTransform>().sizeDelta = new Vector3(0,((i/3)+1) * _rt.sizeDelta.y * _rt.localScale.y);
	}

	// Adds a unit to the screen
	private void AddUnit(int i, UnitData unitData) {
		// Instantiate GameObject, reposition based on index, assign specific game data, and resize scrollable area
		GameObject _unit = Instantiate(Resources.Load("Prefabs/TeamSelect/Unit"), Vector3.zero, Quaternion.identity, GameObject.Find("UnitTabContent").transform) as GameObject;
		RectTransform _rt = _unit.GetComponent<RectTransform>();
		_rt.anchoredPosition = new Vector3(0,-i * _rt.sizeDelta.y * _rt.localScale.y);
		_unit.GetComponent<SelectUnitController>().AssignUnit(unitData);
		GameObject.Find("UnitTabContent").GetComponent<RectTransform>().sizeDelta = new Vector3(0,(i+1) * _rt.sizeDelta.y * _rt.localScale.y);
	}

	// Adds a perk to the screen
	private void AddPerk(int i, PerkData perkData) {
		// Instantiate GameObject, reposition based on index, assign specific game data, and resize scrollable area
		GameObject _perk = Instantiate(Resources.Load("Prefabs/TeamSelect/Perk"), Vector3.zero, Quaternion.identity, GameObject.Find("PerkTabContent").transform) as GameObject;
		RectTransform _rt = _perk.GetComponent<RectTransform>();
		_rt.anchoredPosition = new Vector3((i % 2) * _rt.sizeDelta.x * _rt.localScale.x, (-i / 2) * _rt.sizeDelta.y * _rt.localScale.y);
		_perk.GetComponent<SelectPerkController>().AssignPerk(perkData);
		GameObject.Find("PerkTabContent").GetComponent<RectTransform>().sizeDelta = new Vector3(0,((i/2)+1) * _rt.sizeDelta.y * _rt.localScale.y);
	}

	// Handles when the Set Team response is returned
	private IEnumerator HandleStResponse(Dictionary<string, object> response){
		if(!Parse.Bool(response["Success"])){
			ErrorMessageText.text = Parse.String(response["Error"]);
			LoadingCircle.Hide();

			yield break;
		}
		Server.FindMatch(this);
	}

	// Handles when the Find Match response is returned
	private IEnumerator HandleFmResponse(Dictionary<string, object> response){
		LoadingCircle.Hide();

		if(!Parse.Bool(response["Success"])) {
			ErrorMessageText.text = Parse.String(response["Error"]);

			yield break;
		}

		// Get time since epoch
		TimeSpan t = DateTime.UtcNow - STC_EPOCH;
		int secondsSinceEpoch = (int)t.TotalSeconds;

		Dictionary<string, object> qData = new Dictionary<string, object>();
		qData["In_Game_Queue"]  = true;
		qData["In_Queue_Since"] = secondsSinceEpoch;
		GameData.SetMatchQueueData(qData);

		SceneManager.LoadSceneAsync("MainMenu", LoadSceneMode.Single);

		yield return null;
	}
}
