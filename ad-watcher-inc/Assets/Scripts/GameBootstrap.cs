using UnityEngine;

namespace AdWatcherInc
{
    public static class GameBootstrap
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Boot()
        {
            if (Object.FindFirstObjectByType<GameController>() != null)
                return;

            var go = new GameObject("AdWatcherGame");
            Object.DontDestroyOnLoad(go);
            go.AddComponent<GameController>();
        }
    }
}
