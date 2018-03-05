using System.Collections;
using UnityEngine;
using UnityEngine.UI;

public class ActionResult: MonoBehaviour{
    private bool _stillAnimating;

    public void Create(Transform spawn, bool isRed, string text){
        GameObject ar = new GameObject("Action Result");
        ar.transform.SetParent(spawn);

        Text arText = ar.AddComponent<Text>();
        arText.text = text;
        arText.color = (isRed)? Color.red: Color.green;
        arText.fontSize = 32;

        _stillAnimating = true;
        StartCoroutine(Animate());
        StartCoroutine(Finish());
    }

    private IEnumerator Animate(){
        yield return new WaitForSeconds(0.5f);

        _stillAnimating = false;
    }

    private IEnumerator Finish(){
        while(_stillAnimating){
            yield return new WaitForEndOfFrame();
        }

        GameObject.Destroy(this);
    }
}
