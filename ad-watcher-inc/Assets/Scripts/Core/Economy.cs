using System;

namespace AdWatcherInc.Core
{
    public static class Economy
    {
        public const double BaseAdDurationSeconds = 5d;
        public const double MinAdDurationSeconds = 0.75d;
        public const double BaseRewardPerAd = 1d;
        public const double BaseAutoplayPerSecond = 0d;
        public const double OfflineEarningsCapSeconds = 8d * 60d * 60d; // 8 hours

        public static double AdDurationSeconds(GameState state)
        {
            var level = state.GetLevel(UpgradeId.FasterAds);
            var duration = BaseAdDurationSeconds * Math.Pow(0.92d, level);
            return Math.Max(MinAdDurationSeconds, duration);
        }

        public static double RewardPerAd(GameState state)
        {
            var cpmLevel = state.GetLevel(UpgradeId.BetterCpm);
            var streams = 1 + state.GetLevel(UpgradeId.ParallelStreams);
            return BaseRewardPerAd * (1d + cpmLevel * 0.35d) * streams;
        }

        public static double AutoplayPerSecond(GameState state)
        {
            var level = state.GetLevel(UpgradeId.Autoplay);
            if (level <= 0)
                return BaseAutoplayPerSecond;

            return 0.15d * level * (1d + state.GetLevel(UpgradeId.BetterCpm) * 0.1d);
        }

        public static bool CanAfford(GameState state, UpgradeDefinition upgrade)
        {
            var cost = upgrade.CostForLevel(state.GetLevel(upgrade.Id));
            return state.Attention >= cost;
        }

        public static bool TryBuy(GameState state, UpgradeDefinition upgrade)
        {
            var level = state.GetLevel(upgrade.Id);
            if (level >= upgrade.MaxLevel)
                return false;

            var cost = upgrade.CostForLevel(level);
            if (state.Attention < cost)
                return false;

            state.Attention -= cost;
            state.SetLevel(upgrade.Id, level + 1);
            return true;
        }

        public static void GrantAttention(GameState state, double amount)
        {
            if (amount <= 0d)
                return;

            state.Attention += amount;
            state.LifetimeAttention += amount;
        }

        public static double ApplyOfflineEarnings(GameState state, long nowUnixMs)
        {
            if (state.LastSaveUnixMs <= 0)
                return 0d;

            var elapsedSeconds = Math.Max(0d, (nowUnixMs - state.LastSaveUnixMs) / 1000d);
            elapsedSeconds = Math.Min(elapsedSeconds, OfflineEarningsCapSeconds);

            var rate = AutoplayPerSecond(state);
            // Also credit a gentle "background ads" drip even without autoplay,
            // so returning players always see the joke.
            var backgroundAdsPerSecond = 0.02d * RewardPerAd(state);
            var totalRate = rate + backgroundAdsPerSecond;
            var earned = totalRate * elapsedSeconds;
            GrantAttention(state, earned);
            return earned;
        }
    }
}
