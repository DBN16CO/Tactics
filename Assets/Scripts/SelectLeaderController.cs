using UnityEngine;
using UnityEngine.UI;

// This class controls each selectable Leader GameObject
public class SelectLeaderController : ParentController {

	public LeaderData data;
	private SetTeamController stc;

	// Controls the image of the selectable GameObject
	public Sprite LeaderImage {
		get{return gameObject.transform.Find("Image").GetComponent<Image>().sprite;}
		set{gameObject.transform.Find("Image").GetComponent<Image>().sprite = value;}
	}
	// Controls the display name text of the selectable GameObject
	public string DisplayName {
		get{return gameObject.transform.Find("Name").GetComponent<Text>().text;}
		set{gameObject.transform.Find("Name").GetComponent<Text>().text = value;}
	}

	// Set specified game data on the selectable GameObject
	public void AssignLeader(LeaderData leaderData) {
		stc = GameObject.Find("SetTeamController").GetComponent<SetTeamController>();
		data = leaderData;
		gameObject.name = data.Name;
		LeaderImage = Resources.Load<Sprite>(data.SpritePath);
		DisplayName = gameObject.name;
	}

	// Select and unselect this leader
	public void ToggleLeader() {
		if(stc.leader != gameObject) {
			if(stc.leader != null) {
				stc.leader.GetComponent<SelectLeaderController>().ToggleLeader();
			}
			stc.leader = gameObject;
			gameObject.GetComponent<Image>().color = Color.grey;
		}else {
			stc.leader = null;
			gameObject.GetComponent<Image>().color = Color.white;
		}
	}

}
