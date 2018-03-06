using System.Collections;
using UnityEngine;
using UnityEngine.UI;

public class ActionResult: MonoBehaviour{
    // Constant variables
    private const float AR_VERTICAL_OFFSET = 80f;
    private const float AR_ASSUMED_CAMERA_INIT_SIZE = 5f;
    private const float AR_INIT_FONT = 100f;

    private static float AR_SCREEN_W_OFFSET;
    private static float AR_SCREEN_H_OFFSET;
    private static RectTransform AR_CANVAS = null;
    private bool _stillAnimating;
    private Transform _unit;

    private RectTransform _rt;
    private Text _text;

    void Update(){
        if(_unit == null){
            return;
        }

        float cameraRatio = (AR_ASSUMED_CAMERA_INIT_SIZE / Camera.main.orthographicSize);

        // Set the object's position
        Vector3 offset = Camera.main.WorldToScreenPoint(_unit.localPosition);
        _rt.anchoredPosition = new Vector3(offset.x - AR_SCREEN_W_OFFSET,
            offset.y - AR_SCREEN_H_OFFSET + (AR_VERTICAL_OFFSET * cameraRatio), 0);

        // Set the object's scale
        _text.fontSize = (int)(AR_INIT_FONT * cameraRatio);
    }

    public static ActionResult Create(Transform unit, bool isRed, string text){
        if(AR_CANVAS == null){
            AR_CANVAS = GameObject.Find("Canvas").GetComponent<RectTransform>();
            AR_SCREEN_W_OFFSET = Screen.width / 2;
            AR_SCREEN_H_OFFSET = Screen.height / 2;
        }

        // Spawn the object
        ActionResult ar = Instantiate<GameObject>(Resources.Load<GameObject>("Prefabs/ActionResult"),
            AR_CANVAS).GetComponent<ActionResult>();

        // Initialize all member variables
        ar.Init(unit);

        float cameraRatio = (AR_ASSUMED_CAMERA_INIT_SIZE / Camera.main.orthographicSize);

        // Set the object's position
        ar._rt = ar.gameObject.GetComponent<RectTransform>();
        Vector3 offset = Camera.main.WorldToScreenPoint(unit.localPosition);
        ar._rt.anchoredPosition = new Vector3(offset.x - AR_SCREEN_W_OFFSET, offset.y -
            AR_SCREEN_H_OFFSET + (AR_VERTICAL_OFFSET * cameraRatio), 0);

        ar._text = ar.gameObject.GetComponent<Text>();
        ar._text.text = text;
        ar._text.color = (isRed)? Color.red: Color.green;

        // Set the object's scale
        ar._text.fontSize = (int)(AR_INIT_FONT * cameraRatio);

        ar.StartCoroutine(ar.Animate());
        ar.StartCoroutine(ar.Finish());

        return ar;
    }

    private void Init(Transform unit){
        _stillAnimating = true;
        _unit = unit;
    }

    private IEnumerator Animate(){
        yield return new WaitForSeconds(0.5f);

        _stillAnimating = false;
    }

    private IEnumerator Finish(){
        while(_stillAnimating){
            yield return new WaitForEndOfFrame();
        }

        GameObject.Destroy(gameObject);
    }
}
