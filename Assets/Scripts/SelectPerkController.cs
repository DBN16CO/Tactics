using UnityEngine;
using UnityEngine.UI;

// This class controls each selectable Perk GameObject
public class SelectPerkController : ParentController {

	public PerkData data;
	private SetTeamController stc;

	// Controls the image of the selectable GameObject
	public Sprite PerkIcon {
		get{return gameObject.transform.Find("Icon").GetComponent<Image>().sprite;}
		set{gameObject.transform.Find("Icon").GetComponent<Image>().sprite = value;}
	}
	// Controls the description text of the selectable GameObject
	public string Description {
		get{return gameObject.transform.Find("Text").GetComponent<Text>().text;}
		set{gameObject.transform.Find("Text").GetComponent<Text>().text = value;}
	}
	// Returns the index of the perk tier
	public int ListTier {
		get{return data.tier-1;}
	}

	// Set specified game data on the selectable GameObject
	public void AssignPerk(PerkData perkData) {
		stc = GameObject.Find("SetTeamController").GetComponent<SetTeamController>();
		data = perkData;
		gameObject.name = data.name;
		PerkIcon = Resources.Load<Sprite>(data.iconSpritePath);
		Description = data.description;
	}

	// Select and unselect this perk
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
