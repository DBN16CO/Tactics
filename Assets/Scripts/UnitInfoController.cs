using UnityEngine;
using UnityEngine.UI;

public class UnitInfoController : MonoBehaviour {

	public Text NameText;
	public Text HPText;
	public RectTransform HPBar;

	private float hpWidth;

	void Start () {
		hpWidth = GameObject.Find("UnitHP").GetComponent<RectTransform>().rect.width;
	}
	
	public void SetUnitInfo(MatchUnit unit) {
		NameText.text = unit.Name;
		HPText.text = "HP " + unit.HP + "/" + GameData.GetUnit(unit.Name).GetStat("HP").Value;
		HPBar.offsetMax = new Vector2(-(hpWidth - (hpWidth * ((float)unit.HP/(float)GameData.GetUnit(unit.Name).GetStat("HP").Value))),0);
	}

	public void RemoveUnitInfo() {
		NameText.text = "";
		HPText.text = "";
		HPBar.offsetMax = new Vector2(0,0);
	}

}
