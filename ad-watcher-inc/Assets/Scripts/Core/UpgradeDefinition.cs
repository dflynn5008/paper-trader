namespace AdWatcherInc.Core
{
    public enum UpgradeId
    {
        FasterAds = 0,
        Autoplay = 1,
        BetterCpm = 2,
        ParallelStreams = 3
    }

    public sealed class UpgradeDefinition
    {
        public UpgradeId Id { get; }
        public string Name { get; }
        public string Description { get; }
        public double BaseCost { get; }
        public double CostGrowth { get; }
        public int MaxLevel { get; }

        public UpgradeDefinition(
            UpgradeId id,
            string name,
            string description,
            double baseCost,
            double costGrowth,
            int maxLevel = 50)
        {
            Id = id;
            Name = name;
            Description = description;
            BaseCost = baseCost;
            CostGrowth = costGrowth;
            MaxLevel = maxLevel;
        }

        public double CostForLevel(int currentLevel)
        {
            return BaseCost * System.Math.Pow(CostGrowth, currentLevel);
        }
    }

    public static class UpgradeCatalog
    {
        public static readonly UpgradeDefinition[] All =
        {
            new UpgradeDefinition(
                UpgradeId.FasterAds,
                "Shorter Skip Timer",
                "Ads finish faster. Efficiency!",
                15d,
                1.35d),
            new UpgradeDefinition(
                UpgradeId.Autoplay,
                "Autoplay",
                "Passive Attention while you 'watch'.",
                40d,
                1.45d),
            new UpgradeDefinition(
                UpgradeId.BetterCpm,
                "Better CPM",
                "Each completed ad pays more.",
                25d,
                1.4d),
            new UpgradeDefinition(
                UpgradeId.ParallelStreams,
                "Multi-Stream",
                "Watch multiple ads at once. Totally fine.",
                120d,
                1.55d,
                10)
        };

        public static UpgradeDefinition Get(UpgradeId id)
        {
            foreach (var upgrade in All)
            {
                if (upgrade.Id == id)
                    return upgrade;
            }

            return All[0];
        }
    }
}
