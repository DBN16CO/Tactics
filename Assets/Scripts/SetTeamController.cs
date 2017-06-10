using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using System.Collections.Generic;

// This class controls the SetTeamController GameObject in the SetTeam scene
public class SetTeamController : MonoBehaviour {

	// The team selected
	public GameObject leader;
	public string ability;
	public List<string> units;
	public List<GameObject> perks;

	private int _fundsRemaining;
	private int _maxFunds;

	// Either sets the text value on the screen or gets the int remaining funds
	public int FundsRemaining {
		get{return _fundsRemaining;}
		set{_fundsRemaining = value;
			GameObject.Find("Funds").transform.FindChild("Amount").GetComponent<Text>().text = "$" + _fundsRemaining + " / " + _maxFunds;}
	}
	// Returns whether selected team is valid or not
	public bool IsValidTeam {
		get{return (leader != null && ability != null && units.Count > 0 && perks.Count > 0);}
	}

	void Start () {
		// Populate LeaderTab
		for(int i = 0; i < GameData.GetLeaders.Count; i++) {
			AddLeader(i, GameData.GetLeaders[i]);
		}
		// Populate UnitTab
		for(int i = 0; i < GameData.GetUnits.Count; i++) {
			AddUnit(i, GameData.GetUnits[i]);
		}
		// Populate PerkTab
		for(int i = 0; i < GameData.GetPerks.Count; i++) {
			AddPerk(i, GameData.GetPerks[i]);
		}

		// Init variables
		leader = null;
		units = new List<string>();
		perks = new List<GameObject>(3) {null,null,null};
		_maxFunds = GameData.Version.maxFunds;
		FundsRemaining = _maxFunds;
	}

	// Runs when the app is closed - attempt to close the websocket cleanly
	void OnApplicationQuit() {
		
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
		// Testing ------------
		if(leader != null) {
			ability = leader.GetComponent<SelectLeaderController>().data.Abilities[0].name;
		}else{
			Debug.Log("Select a leader, dick.");
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
			if(Server.SetTeam(strLeader, ability, units, strPerks)) {
				if(!Server.FindMatch()) {
					Debug.Log("Couldn't add to game queue - are you already in queue?");
				}
				Debug.Log("Team set successfully");
				SceneManager.LoadSceneAsync("MainMenu", LoadSceneMode.Single);
			}else {
				Debug.Log("Server error setting team");
			}
		}else{
			Debug.Log("Invalid team");
		}
	}

}
