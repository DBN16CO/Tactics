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
	public Text myMissText;
	public Text targDmgText;
	public Text targCritText;
	public Text targMissText;

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
		// Set unit stats
		UnitData myUnit = GameData.GetUnit(GameController.SelectedToken.CurrentUnit.name);
		int myPower = myUnit.GetStat("Strength").Value;
		int myDef	= myUnit.GetStat("Defense").Value;
		int myAgil	= myUnit.GetStat("Agility").Value;
		int myLuck	= myUnit.GetStat("Luck").Value;
		UnitData targUnit = GameData.GetUnit(GameController.IntendedTarget.CurrentUnit.name);
		int targPower 	= targUnit.GetStat("Strength").Value;
		int targDef		= targUnit.GetStat("Defense").Value;
		int targAgil	= targUnit.GetStat("Agility").Value;
		int targLuck	= targUnit.GetStat("Luck").Value; 
		// Calculate vars
		int myDmg 	= Mathf.Max(0, myPower - targDef);
		int myMiss 	= Mathf.Max(0, ((targAgil - myAgil) * 5) + 5);
		int myCrit 	= Mathf.Max(0, ((myLuck - targLuck) * 5) + 5);
		int targDmg 	= Mathf.Max(0, targPower - myDef);
		int targMiss 	= Mathf.Max(0, ((myAgil - targAgil) * 5) + 5);
		int targCrit 	= Mathf.Max(0, ((targLuck - myLuck) * 5) + 5);
		// Update text
		myDmgText.text 	= myDmg.ToString();
		myMissText.text = myMiss.ToString();
		myCritText.text = myCrit.ToString();
		targDmgText.text	= targDmg.ToString();
		targMissText.text	= targMiss.ToString();
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
}
