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
	public void SetUnitInfo(Unit unit) {
		NameText.text = unit.UnitName;

		int maxHP = GameData.GetUnit(unit.UnitName).GetStat("HP").Value;
		HPText.text = unit.HP + "/" + maxHP;
		HPBar.offsetMax = new Vector2( -(hpWidth - (hpWidth * ((float)unit.HP / (float)maxHP))), 0);
	}

	// Clears info
	public void RemoveUnitInfo() {
		NameText.text = "";
		HPText.text = "";
		HPBar.offsetMax = new Vector2(0,0);
	}

}
