using UnityEngine;
using UnityEngine.UI;

public class SelectLeaderController : MonoBehaviour {

	private LeaderData _data;
	private SetTeamController stc;

	public Sprite LeaderImage {
		get{return gameObject.transform.FindChild("Image").GetComponent<Image>().sprite;}
		set{gameObject.transform.FindChild("Image").GetComponent<Image>().sprite = value;}
	}
	public string DisplayName {
		get{return gameObject.transform.FindChild("Name").GetComponent<Text>().text;}
		set{gameObject.transform.FindChild("Name").GetComponent<Text>().text = value;}
	}

	public void AssignLeader(LeaderData leaderData) {
		stc = GameObject.Find("SetTeamController").GetComponent<SetTeamController>();
		_data = leaderData;
		gameObject.name = _data.name;
		LeaderImage = Resources.Load<Sprite>(_data.spritePath);
		DisplayName = gameObject.name;
	}

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
