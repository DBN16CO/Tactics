using UnityEngine;

public class SetTeamController : MonoBehaviour {

	void Start () {
		// For quick testing starting from this scene - need to load data
		if(GameData.Player == null) {
			Server.Connect();
			Server.Login("nickpriore", "tactics");
			Server.GetUserInfo();
			if(!Server.InitialLoad()) {Debug.Log("IL failed"); return;}
		}
		//---------------------------------------------------------------

		// Populate LeaderTab
		int mult = 5; int count = GameData.GetLeaders.Count;
		for(int i = 0; i < count * mult; i++) {
			AddLeader(i, GameData.GetLeaders[i % count]);
		}
		// Populate UnitTab
		for(int i = 0; i < GameData.GetUnits.Count; i++) {
			AddUnit(GameData.GetUnits[i]);
		}
		// Populate PerkTab
		for(int i = 0; i < GameData.GetPerks.Count; i++) {
			AddPerk(i, GameData.GetPerks[i]);
		}
	}

	void Update () {

	}

	private void AddLeader(int i, LeaderData leaderData) {
		GameObject leader = Instantiate(Resources.Load("Prefabs/TeamSelect/Leader"), Vector3.zero, Quaternion.identity, GameObject.Find("LeaderTabContent").transform) as GameObject;
		RectTransform _rt = leader.GetComponent<RectTransform>();
		_rt.anchoredPosition = new Vector3((i % 3) * _rt.sizeDelta.x * _rt.localScale.x, (-i / 3) * _rt.sizeDelta.y * _rt.localScale.y);
		leader.GetComponent<SelectLeaderController>().AssignLeader(leaderData);
		GameObject.Find("LeaderTabContent").GetComponent<RectTransform>().sizeDelta = new Vector3(0,((i/3)+1) * _rt.sizeDelta.y * _rt.localScale.y);
	}

	private void AddUnit(UnitData unitData) {

	}

	private void AddPerk(int i, PerkData perkData) {
		GameObject perk = Instantiate(Resources.Load("Prefabs/TeamSelect/Perk"), Vector3.zero, Quaternion.identity, GameObject.Find("PerkTabContent").transform) as GameObject;
		RectTransform _rt = perk.GetComponent<RectTransform>();
		_rt.anchoredPosition = new Vector3((i % 2) * _rt.sizeDelta.x * _rt.localScale.x, (-i / 2) * _rt.sizeDelta.y * _rt.localScale.y);
		perk.GetComponent<SelectPerkController>().AssignPerk(perkData);
		GameObject.Find("PerkTabContent").GetComponent<RectTransform>().sizeDelta = new Vector3(0,((i/2)+1) * _rt.sizeDelta.y * _rt.localScale.y);
	}

}
