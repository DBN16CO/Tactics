using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using System.Collections.Generic;

// This class controls the SetTeamController GameObject in the SetTeam scene
public class SetTeamController : ParentController {

	// The team selected
	public GameObject leader;
	public string ability;
	public List<string> units;
	public List<GameObject> perks;

	private int _fundsRemaining;
	private int _maxFunds;

	public static Text ErrorMessageText;

	// Either sets the text value on the screen or gets the int remaining funds
	public int FundsRemaining {
		get{return _fundsRemaining;}
		set{_fundsRemaining = value;
			GameObject.Find("Funds").transform.Find("Amount").GetComponent<Text>().text = "$" + _fundsRemaining + " / " + _maxFunds;}
	}
	// Returns whether selected team is valid or not
	public bool IsValidTeam {
		get{return (leader != null && ability != null && units.Count > 0 && perks.Count > 0);}
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

	// Passes selected team to the database
	public void SetTeam() {
		ErrorMessageText.text = "";

		// Testing ------------
		if(leader != null) {
			LeaderData data = leader.GetComponent<SelectLeaderController>().data;
			List<string> strAbilities = new List<string>(data.Abilities.Keys);
			ability = data.Abilities[strAbilities[0]].Name;
		}else{
			Debug.Log("Select a leader.");
			return;
		}
		// End Testing --------

		if(IsValidTeam) {
			string strLeader = leader.name;
			List<string> strPerks = new List<string>();
			foreach(GameObject obj in perks) {
				if(obj != null) {
					strPerks.Add(obj.name);
				}
			}

			Dictionary<string, object> response = Server.SetTeam(strLeader, ability, units, strPerks);
			if(Parse.Bool(response["Success"])){
				Dictionary<string, object> fmResponse = Server.FindMatch();
				if(! Parse.Bool(fmResponse["Success"])) {
					ErrorMessageText.text = Parse.String(fmResponse["Error"]);
					Debug.Log("Couldn't add to game queue - are you already in queue?");
				}
				Debug.Log("Team set successfully");
				SceneManager.LoadSceneAsync("MainMenu", LoadSceneMode.Single);
			}
			else{
				ErrorMessageText.text = Parse.String(response["Error"]);
				Debug.Log("Server error setting team");
			}
		}else{
			Debug.Log("Invalid team");
		}
	}

	public void BackToMainMenu(){
		ErrorMessageText.text = "";
		SceneManager.LoadSceneAsync("MainMenu", LoadSceneMode.Single);
	}

}
