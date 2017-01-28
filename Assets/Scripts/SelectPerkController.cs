using UnityEngine;
using UnityEngine.UI;

public class SelectPerkController : MonoBehaviour {

	public Sprite PerkIcon {
		get{return gameObject.transform.FindChild("Icon").GetComponent<Image>().sprite;}
		set{gameObject.transform.FindChild("Icon").GetComponent<Image>().sprite = value;}
	}
	public string Description {
		get{return gameObject.transform.FindChild("Text").GetComponent<Text>().text;}
		set{gameObject.transform.FindChild("Text").GetComponent<Text>().text = value;}
	}

	public void AssignPerk(PerkData perkData) {
		gameObject.name = perkData.name;
		PerkIcon = Resources.Load<Sprite>(perkData.iconSpritePath);
		Description = perkData.description;
	}
}
