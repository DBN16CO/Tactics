using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

public class SetTeamController : MonoBehaviour {

	public GameObject leader;
	public List<string> units;
	public List<GameObject> perks;

	private int _fundsRemaining;
	private int _maxFunds;

	public int FundsRemaining {
		get{return _fundsRemaining;}
		set{_fundsRemaining = value;
			GameObject.Find("Funds").transform.FindChild("Amount").GetComponent<Text>().text = "$" + _fundsRemaining + " / " + _maxFunds;}
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
		_maxFunds = GameData.Match.maxFunds;
		FundsRemaining = _maxFunds;


	}

	private void AddLeader(int i, LeaderData leaderData) {
		GameObject leader = Instantiate(Resources.Load("Prefabs/TeamSelect/Leader"), Vector3.zero, Quaternion.identity, GameObject.Find("LeaderTabContent").transform) as GameObject;
		RectTransform _rt = leader.GetComponent<RectTransform>();
		_rt.anchoredPosition = new Vector3((i % 3) * _rt.sizeDelta.x * _rt.localScale.x, (-i / 3) * _rt.sizeDelta.y * _rt.localScale.y);
		leader.GetComponent<SelectLeaderController>().AssignLeader(leaderData);
		GameObject.Find("LeaderTabContent").GetComponent<RectTransform>().sizeDelta = new Vector3(0,((i/3)+1) * _rt.sizeDelta.y * _rt.localScale.y);
	}

	private void AddUnit(int i, UnitData unitData) {
		GameObject unit = Instantiate(Resources.Load("Prefabs/TeamSelect/Unit"), Vector3.zero, Quaternion.identity, GameObject.Find("UnitTabContent").transform) as GameObject;
		RectTransform _rt = unit.GetComponent<RectTransform>();
		_rt.anchoredPosition = new Vector3(0,-i * _rt.sizeDelta.y * _rt.localScale.y);
		unit.GetComponent<SelectUnitController>().AssignUnit(unitData);
		GameObject.Find("UnitTabContent").GetComponent<RectTransform>().sizeDelta = new Vector3(0,(i+1) * _rt.sizeDelta.y * _rt.localScale.y);
	}

	private void AddPerk(int i, PerkData perkData) {
		GameObject perk = Instantiate(Resources.Load("Prefabs/TeamSelect/Perk"), Vector3.zero, Quaternion.identity, GameObject.Find("PerkTabContent").transform) as GameObject;
		RectTransform _rt = perk.GetComponent<RectTransform>();
		_rt.anchoredPosition = new Vector3((i % 2) * _rt.sizeDelta.x * _rt.localScale.x, (-i / 2) * _rt.sizeDelta.y * _rt.localScale.y);
		perk.GetComponent<SelectPerkController>().AssignPerk(perkData);
		GameObject.Find("PerkTabContent").GetComponent<RectTransform>().sizeDelta = new Vector3(0,((i/2)+1) * _rt.sizeDelta.y * _rt.localScale.y);
	}

}
