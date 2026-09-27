using System;
using System.IO;
using UnityEngine;

namespace AdWatcherInc.Core
{
    public static class SaveSystem
    {
        private const string FileName = "ad_watcher_save.json";

        private static string FilePath => Path.Combine(Application.persistentDataPath, FileName);

        public static void Save(GameState state)
        {
            state.LastSaveUnixMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            var json = JsonUtility.ToJson(state, true);
            File.WriteAllText(FilePath, json);
        }

        public static GameState LoadOrCreate()
        {
            try
            {
                if (!File.Exists(FilePath))
                    return NewState();

                var json = File.ReadAllText(FilePath);
                var state = JsonUtility.FromJson<GameState>(json);
                if (state == null)
                    return NewState();

                EnsureUpgradeArray(state);
                return state;
            }
            catch (Exception e)
            {
                Debug.LogWarning("Save load failed, starting fresh: " + e.Message);
                return NewState();
            }
        }

        public static void Delete()
        {
            if (File.Exists(FilePath))
                File.Delete(FilePath);
        }

        private static GameState NewState()
        {
            var state = new GameState
            {
                Attention = 0d,
                LifetimeAttention = 0d,
                TotalAdsWatched = 0,
                LastSaveUnixMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                UpgradeLevels = new int[UpgradeCatalog.All.Length]
            };
            return state;
        }

        private static void EnsureUpgradeArray(GameState state)
        {
            if (state.UpgradeLevels != null && state.UpgradeLevels.Length == UpgradeCatalog.All.Length)
                return;

            var resized = new int[UpgradeCatalog.All.Length];
            if (state.UpgradeLevels != null)
            {
                Array.Copy(
                    state.UpgradeLevels,
                    resized,
                    Math.Min(state.UpgradeLevels.Length, resized.Length));
            }

            state.UpgradeLevels = resized;
        }
    }
}
