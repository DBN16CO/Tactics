using UnityEngine;

public class LoadingCircle : MonoBehaviour
{
    private const float ROTATE_SPEED = 400f;

    private static GameObject go;
    private static RectTransform rectComponent;

    private void Start()
    {
        go = GameObject.Find("LoadingCircle");
        rectComponent = go.gameObject.transform.Find("Progress").GetComponent<RectTransform>();
        go.SetActive(false);
    }

    private void Update()
    {
        rectComponent.Rotate(0f, 0f, - ROTATE_SPEED * Time.deltaTime);
    }

    public static void Hide(){
        go.SetActive(false);
    }

    public static void Show(){
        go.SetActive(true);
    }
}
