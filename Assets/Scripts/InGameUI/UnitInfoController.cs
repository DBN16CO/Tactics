using UnityEngine;
using UnityEngine.UI;

public class UnitInfoController : MonoBehaviour {

	public Text NameText;			// Name of the unit
	public Text HPText;				// HP of the unit
	public RectTransform HPBar;		// Transform of the hp bar

	private float hpWidth;			// Reference to the width of the HP bar (apparent height since it's rotated in the scene)

	void Start () {
		hpWidth = gameObject.transform.Find("UnitHP").GetComponent<RectTransform>().rect.width;
	}
	
	// Sets necessary info
	public void SetUnitInfo(UnitInfo unit) {
		NameText.text = unit.Name;
		HPText.text = unit.HP + "/" + GameData.GetUnits[unit.Name].GetStats["HP"].Value;
		HPBar.offsetMax = new Vector2(-(hpWidth - (hpWidth * ((float)unit.HP/(float)GameData.GetUnits[unit.Name].GetStats["HP"].Value))),0);
	}

	// Clears info
	public void RemoveUnitInfo() {
		NameText.text = "";
		HPText.text = "";
		HPBar.offsetMax = new Vector2(0,0);
	}

}
