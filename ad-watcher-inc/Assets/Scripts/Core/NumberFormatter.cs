using System;
using System.Globalization;

namespace AdWatcherInc.Core
{
    public static class NumberFormatter
    {
        private static readonly string[] Suffixes =
        {
            "", "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc"
        };

        public static string Format(double value)
        {
            if (double.IsNaN(value) || double.IsInfinity(value))
                return "0";

            var sign = value < 0 ? "-" : "";
            value = Math.Abs(value);

            if (value < 1000d)
                return sign + Math.Floor(value).ToString("0", CultureInfo.InvariantCulture);

            var tier = Math.Min(Suffixes.Length - 1, (int)Math.Floor(Math.Log10(value) / 3d));
            var scaled = value / Math.Pow(1000d, tier);
            return sign + scaled.ToString("0.##", CultureInfo.InvariantCulture) + Suffixes[tier];
        }
    }
}
