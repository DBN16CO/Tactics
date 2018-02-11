using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class UIAnimations : MonoBehaviour {

	public void UIPop() {
		gameObject.GetComponent<RectTransform>().localScale += new Vector3(.1f,.1f,0);
	}
	public void UIUnpop() {
		gameObject.GetComponent<RectTransform>().localScale -= new Vector3(.1f,.1f,0);
	}

}
