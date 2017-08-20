using UnityEngine;
using UnityEngine.UI;

public class TargetDetailsController : MonoBehaviour {

	// Static reference to self
	public static TargetDetailsController Main;

	// Lerp until difference in position and target position is under threshold
	private const float LERP_THRESHOLD 			= 1f;
	private const float TARGET_Y				= -220f;

	private float _timer;			// Measure of time
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

		_timer = 0;
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
		UnitData myUnit 	= GameData.GetUnits[GameController.SelectedToken.CurrentUnit.Info.Name];
		UnitData targUnit 	= GameData.GetUnits[GameController.IntendedTarget.CurrentUnit.Info.Name];
		// DEVELOPMENT UNTIL BETTER WAY TO DETERMINE PHYSICAL VS MAGICAL
		bool myPhysical 	= myUnit.GetStats["Strength"].Value > myUnit.GetStats["Intelligence"].Value;

		int myPower 	= (myPhysical)? myUnit.GetStats["Strength"].Value : myUnit.GetStats["Intelligence"].Value;
		int myAgil		= myUnit.GetStats["Agility"].Value;
		int myLuck		= myUnit.GetStats["Luck"].Value;
		int targDef		= (myPhysical)? targUnit.GetStats["Defense"].Value : targUnit.GetStats["Resistance"].Value;
		int targAgil	= targUnit.GetStats["Agility"].Value;
		int targLuck	= targUnit.GetStats["Luck"].Value;

		// Calculate vars
		int myDmg 	= Mathf.Max(0, myPower - targDef);
		int myHit 	= (IsAttack)? 100 - Mathf.Max(0, ((targAgil - myAgil) * 5) + 5) : 100;
		int myCrit 	= (IsAttack)? Mathf.Max(0, ((myLuck - targLuck) * 5) + 5) : 0;

		int targDmg; int targHit; int targCrit;
		if(GameController.Main.CanTargetCounter() && IsAttack) {
			bool targPhysical	= targUnit.GetStats["Strength"].Value > targUnit.GetStats["Intelligence"].Value;
			int myDef	= (targPhysical)? myUnit.GetStats["Defense"].Value : myUnit.GetStats["Resistance"].Value;
			int targPower 	= (targPhysical)? targUnit.GetStats["Strength"].Value : targUnit.GetStats["Intelligence"].Value;
			
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
