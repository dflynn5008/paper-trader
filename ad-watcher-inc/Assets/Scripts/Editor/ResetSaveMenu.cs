#if UNITY_EDITOR
using AdWatcherInc.Core;
using UnityEditor;
using UnityEngine;

namespace AdWatcherInc.EditorTools
{
    public static class ResetSaveMenu
    {
        [MenuItem("Ad Watcher/Reset Save Data")]
        private static void ResetSave()
        {
            SaveSystem.Delete();
            Debug.Log("Ad Watcher save deleted at " + Application.persistentDataPath);
        }
    }
}
#endif
