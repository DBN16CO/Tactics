using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEngine.UI;
using UnityEditor.UI;

[CustomEditor(typeof(ScrollRectNested))]
public class ScrollRectNestedEditor : ScrollRectEditor
{
    SerializedProperty parentScrollRectProp;
    SerializedProperty parentScrollSnapProp;
    GUIContent parentScrollRectGUIContent = new GUIContent("Parent ScrollRect");
    GUIContent parentScrollSnapGUIContent = new GUIContent("Parent ScrollSnap");

    protected override void OnEnable()
    {
        base.OnEnable();
        parentScrollRectProp = serializedObject.FindProperty("parentScrollRect");
        parentScrollSnapProp = serializedObject.FindProperty("parentScrollSnap");
    }

    public override void OnInspectorGUI()
    {
        base.OnInspectorGUI();
        serializedObject.Update();
        EditorGUILayout.PropertyField(parentScrollRectProp, parentScrollRectGUIContent);
        EditorGUILayout.PropertyField(parentScrollSnapProp, parentScrollSnapGUIContent);
        serializedObject.ApplyModifiedProperties();
    }
}

