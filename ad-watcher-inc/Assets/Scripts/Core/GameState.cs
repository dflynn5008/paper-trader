using System;

namespace AdWatcherInc.Core
{
    [Serializable]
    public sealed class GameState
    {
        public double Attention;
        public double LifetimeAttention;
        public long TotalAdsWatched;
        public int[] UpgradeLevels = new int[UpgradeCatalog.All.Length];
        public long LastSaveUnixMs;
        public string LastAdHeadline = "";

        public int GetLevel(UpgradeId id)
        {
            var index = (int)id;
            if (index < 0 || index >= UpgradeLevels.Length)
                return 0;
            return UpgradeLevels[index];
        }

        public void SetLevel(UpgradeId id, int level)
        {
            var index = (int)id;
            if (index < 0 || index >= UpgradeLevels.Length)
                return;
            UpgradeLevels[index] = level;
        }
    }
}
