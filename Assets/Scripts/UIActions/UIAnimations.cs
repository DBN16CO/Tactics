using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class UIAnimations : MonoBehaviour {

	public bool moving;

	private float _t;


	// Update is called once per frame
	void Update () {
		//_t += Time.deltaTime;
	}

	public void SelectPU() {
		gameObject.GetComponent<RectTransform>().localScale += new Vector3(.1f,.1f,0);
	}
	public void UnselectPU() {
		gameObject.GetComponent<RectTransform>().localScale -= new Vector3(.1f,.1f,0);
	}

}
