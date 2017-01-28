using UnityEngine;
using UnityEngine.UI;

public class SelectLeaderController : MonoBehaviour {

	public Sprite LeaderImage {
		get{return gameObject.transform.FindChild("Image").GetComponent<Image>().sprite;}
		set{gameObject.transform.FindChild("Image").GetComponent<Image>().sprite = value;}
	}
	public string DisplayName {
		get{return gameObject.transform.FindChild("Name").GetComponent<Text>().text;}
		set{gameObject.transform.FindChild("Name").GetComponent<Text>().text = value;}
	}

	public void AssignLeader(LeaderData leaderData) {
		gameObject.name = leaderData.name;
		LeaderImage = Resources.Load<Sprite>(leaderData.spritePath);
		DisplayName = gameObject.name;
	}

}
