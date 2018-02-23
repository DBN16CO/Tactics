using UnityEngine;
using UnityEngine.UI;

public class TargetDetailsController : MonoBehaviour {

	// Static reference to self
	public static TargetDetailsController Main;

	// Lerp until difference in position and target position is under threshold
	private const float LERP_THRESHOLD 			= 1f;
	private const float TARGET_Y				= -220f;

	private RectTransform _rt;		// Reference to RectTransform to speed up processing

	// Object references
	public Text myDmgText;
	public Text myCritText;
	public Text myHitText;
	public Text targDmgText;
	public Text targCritText;
	public Text targHitText;

	public Text DmgOrHeal;

	void Start () {
		Main = this;

		_rt = gameObject.GetComponent<RectTransform>();
	}

	void Update () {
		if(ToLerp) {
			// Lerp from current position to target position
			_rt.anchoredPosition = Vector2.Lerp(_rt.anchoredPosition, new Vector2(0f, TargetY), Time.deltaTime * 20f);
		}
	}

	// Updates details when target is selected
	public void SetDetails() {
		// Update dmg or heal text
		DmgOrHeal.text = (IsAttack)? "DMG" : "HEAL";
		// Set unit stats
		UnitData myUnit 	= GameData.GetUnit(GameController.SelectedToken.CurrentUnit.UnitName);
		UnitData targUnit 	= GameData.GetUnit(GameController.IntendedTarget.CurrentUnit.UnitName);
		// DEVELOPMENT UNTIL BETTER WAY TO DETERMINE PHYSICAL VS MAGICAL
		bool myPhysical 	= myUnit.GetStat("Strength").Value > myUnit.GetStat("Intelligence").Value;

		int myPower 	= (myPhysical)? myUnit.GetStat("Strength").Value : myUnit.GetStat("Intelligence").Value;
		int myAgil		= myUnit.GetStat("Agility").Value;
		int myLuck		= myUnit.GetStat("Luck").Value;
		int targDef		= (myPhysical)? targUnit.GetStat("Defense").Value : targUnit.GetStat("Resistance").Value;
		int targAgil	= targUnit.GetStat("Agility").Value;
		int targLuck	= targUnit.GetStat("Luck").Value;

		// Calculate vars
		int myDmg 	= Mathf.Max(0, myPower - targDef);
		int myHit 	= (IsAttack)? 100 - Mathf.Max(0, ((targAgil - myAgil) * 5) + 5) : 100;
		int myCrit 	= (IsAttack)? Mathf.Max(0, ((myLuck - targLuck) * 5) + 5) : 0;

		int targDmg; int targHit; int targCrit;
		if(GameController.CanTargetCounter() && IsAttack) {
			bool targPhysical	= targUnit.GetStat("Strength").Value > targUnit.GetStat("Intelligence").Value;
			int myDef	= (targPhysical)? myUnit.GetStat("Defense").Value : myUnit.GetStat("Resistance").Value;
			int targPower 	= (targPhysical)? targUnit.GetStat("Strength").Value : targUnit.GetStat("Intelligence").Value;

			targDmg 	= Mathf.Max(0, targPower - myDef);
			targHit 	= 100 - Mathf.Max(0, ((myAgil - targAgil) * 5) + 5);
			targCrit 	= Mathf.Max(0, ((targLuck - myLuck) * 5) + 5);
		}else {
			targDmg 	= 0;
			targHit 	= 0;
			targCrit 	= 0;
		}

		// Update text
		myDmgText.text 	= myDmg.ToString();
		myHitText.text = myHit.ToString();
		myCritText.text = myCrit.ToString();
		targDmgText.text	= targDmg.ToString();
		targHitText.text	= targHit.ToString();
		targCritText.text	= targCrit.ToString();
	}

	// Determine whether to lerp
	private bool ToLerp {
		get{return Mathf.Abs(TargetY - _rt.anchoredPosition.y) > LERP_THRESHOLD;}
	}
	// Returns target Y position based on existence of IntendedTarget
	private float TargetY {
		get{return TARGET_Y * ((GameController.IntendedTarget == null)? -1f : 1f);}
	}
	// Determine whether healing or attacking
	private bool IsAttack {
		get{return !GameController.IntendedTarget.CurrentUnit.MyTeam;}
	}
}
