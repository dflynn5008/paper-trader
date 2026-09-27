using System;

namespace AdWatcherInc.Core
{
    public static class FakeAdCopy
    {
        private static readonly string[] Headlines =
        {
            "Dentists HATE this one Attention hack",
            "Download Farm Saga Legend Royale — Free*",
            "Your inventory is full. Buy more slots?",
            "Congrats! You're visitor #1,000,000",
            "Single COOs in your area are hiring",
            "This VPN protects you from other ads",
            "Learn AdOps in 3 minutes (not really)",
            "Rate us 5 stars to skip this ad",
            "Unskippable synergy awaits",
            "Install now — continue watching later"
        };

        private static readonly string[] Brands =
        {
            "GlowBean™", "TapForge", "CloudNibble", "SynergyLoot",
            "QuietPhone Case Co.", "MetricBeans", "ScrollVault", "PromoGoblin"
        };

        public static string NextHeadline(Random rng)
        {
            var brand = Brands[rng.Next(Brands.Length)];
            var line = Headlines[rng.Next(Headlines.Length)];
            return brand + " — " + line;
        }
    }
}
