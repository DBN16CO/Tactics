using UnityEngine;
using UnityEngine.UI;

public class SelectPerkController : MonoBehaviour {

	private PerkData _data;
	private SetTeamController stc;

	public Sprite PerkIcon {
		get{return gameObject.transform.FindChild("Icon").GetComponent<Image>().sprite;}
		set{gameObject.transform.FindChild("Icon").GetComponent<Image>().sprite = value;}
	}
	public string Description {
		get{return gameObject.transform.FindChild("Text").GetComponent<Text>().text;}
		set{gameObject.transform.FindChild("Text").GetComponent<Text>().text = value;}
	}

	public int ListTier {
		get{return _data.tier-1;}
	}

	public void AssignPerk(PerkData perkData) {
		stc = GameObject.Find("SetTeamController").GetComponent<SetTeamController>();
		_data = perkData;
		gameObject.name = _data.name;
		PerkIcon = Resources.Load<Sprite>(_data.iconSpritePath);
		Description = _data.description;
	}

	public void TogglePerk() {
		if(stc.perks[ListTier] != gameObject) {
			if(stc.perks[ListTier] != null) {
				stc.perks[ListTier].GetComponent<SelectPerkController>().TogglePerk();
			}
			stc.perks[ListTier] = gameObject;
			gameObject.GetComponent<Image>().color = Color.grey;
		}else {
			stc.perks[ListTier] = null;
			gameObject.GetComponent<Image>().color = Color.white;
		}
	}

}
