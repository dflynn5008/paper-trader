using System;
using AdWatcherInc.Core;
using UnityEngine;
using UnityEngine.UI;

namespace AdWatcherInc.UI
{
    public sealed class GameHud
    {
        public event Action WatchClicked;
        public event Action<UpgradeId> UpgradeClicked;
        public event Action DismissOffline;

        private Text _brand;
        private Text _attention;
        private Text _stats;
        private Text _watchLabel;
        private Text _status;
        private Button _watchButton;
        private Image _watchImage;
        private readonly Button[] _upgradeButtons = new Button[UpgradeCatalog.All.Length];
        private readonly Text[] _upgradeLabels = new Text[UpgradeCatalog.All.Length];
        private readonly Image[] _upgradeImages = new Image[UpgradeCatalog.All.Length];

        private GameObject _adOverlay;
        private Text _adHeadline;
        private Text _adTimer;
        private Image _adProgressFill;

        private GameObject _offlineOverlay;
        private Text _offlineBody;

        public void Build(Transform root)
        {
            UiFactory.CreatePanel(root, "Background", GameTheme.Background);

            _brand = UiFactory.CreateText(
                root,
                "Brand",
                "AD WATCHER INC.",
                64,
                GameTheme.TextPrimary,
                FontStyle.Bold,
                TextAnchor.MiddleCenter);
            UiFactory.SetRect(_brand.rectTransform, new Vector2(0.06f, 0.86f), new Vector2(0.94f, 0.96f), Vector2.zero, Vector2.zero);

            var tagline = UiFactory.CreateText(
                root,
                "Tagline",
                "Tap. Watch. Ascend.",
                28,
                GameTheme.TextMuted,
                FontStyle.Normal,
                TextAnchor.MiddleCenter);
            UiFactory.SetRect(tagline.rectTransform, new Vector2(0.1f, 0.81f), new Vector2(0.9f, 0.87f), Vector2.zero, Vector2.zero);

            _attention = UiFactory.CreateText(
                root,
                "Attention",
                "0 Attention",
                52,
                GameTheme.AccentLime,
                FontStyle.Bold,
                TextAnchor.MiddleCenter);
            UiFactory.SetRect(_attention.rectTransform, new Vector2(0.08f, 0.72f), new Vector2(0.92f, 0.8f), Vector2.zero, Vector2.zero);

            _stats = UiFactory.CreateText(
                root,
                "Stats",
                "Ads watched: 0",
                24,
                GameTheme.TextMuted,
                FontStyle.Normal,
                TextAnchor.MiddleCenter);
            UiFactory.SetRect(_stats.rectTransform, new Vector2(0.08f, 0.67f), new Vector2(0.92f, 0.72f), Vector2.zero, Vector2.zero);

            _watchButton = UiFactory.CreateButton(root, "WatchButton", GameTheme.CtaOrange);
            UiFactory.SetRect(
                _watchButton.GetComponent<RectTransform>(),
                new Vector2(0.12f, 0.52f),
                new Vector2(0.88f, 0.64f),
                Vector2.zero,
                Vector2.zero);
            _watchImage = _watchButton.GetComponent<Image>();
            _watchLabel = UiFactory.CreateText(
                _watchButton.transform,
                "Label",
                "WATCH AD",
                40,
                Color.white,
                FontStyle.Bold,
                TextAnchor.MiddleCenter);
            UiFactory.Stretch(_watchLabel.rectTransform);
            _watchButton.onClick.AddListener(() => WatchClicked?.Invoke());

            _status = UiFactory.CreateText(
                root,
                "Status",
                "First upgrade unlocks in a few taps.",
                22,
                GameTheme.TextMuted,
                FontStyle.Italic,
                TextAnchor.MiddleCenter);
            UiFactory.SetRect(_status.rectTransform, new Vector2(0.08f, 0.46f), new Vector2(0.92f, 0.51f), Vector2.zero, Vector2.zero);

            var upgradesHeader = UiFactory.CreateText(
                root,
                "UpgradesHeader",
                "UPGRADES",
                26,
                GameTheme.TextPrimary,
                FontStyle.Bold,
                TextAnchor.MiddleLeft);
            UiFactory.SetRect(upgradesHeader.rectTransform, new Vector2(0.1f, 0.41f), new Vector2(0.9f, 0.46f), Vector2.zero, Vector2.zero);

            for (var i = 0; i < UpgradeCatalog.All.Length; i++)
            {
                var upgrade = UpgradeCatalog.All[i];
                var button = UiFactory.CreateButton(root, "Upgrade_" + upgrade.Id, GameTheme.Panel);
                var yMax = 0.40f - i * 0.09f;
                var yMin = yMax - 0.08f;
                UiFactory.SetRect(
                    button.GetComponent<RectTransform>(),
                    new Vector2(0.08f, yMin),
                    new Vector2(0.92f, yMax),
                    Vector2.zero,
                    Vector2.zero);

                var label = UiFactory.CreateText(
                    button.transform,
                    "Label",
                    upgrade.Name,
                    24,
                    GameTheme.TextPrimary,
                    FontStyle.Normal,
                    TextAnchor.MiddleLeft);
                UiFactory.SetRect(label.rectTransform, new Vector2(0.04f, 0.1f), new Vector2(0.96f, 0.9f), Vector2.zero, Vector2.zero);

                var captured = upgrade.Id;
                button.onClick.AddListener(() => UpgradeClicked?.Invoke(captured));
                _upgradeButtons[i] = button;
                _upgradeLabels[i] = label;
                _upgradeImages[i] = button.GetComponent<Image>();
            }

            BuildAdOverlay(root);
            BuildOfflineOverlay(root);
        }

        private void BuildAdOverlay(Transform root)
        {
            _adOverlay = UiFactory.CreatePanel(root, "AdOverlay", GameTheme.AdOverlay).gameObject;
            _adOverlay.SetActive(false);

            var card = UiFactory.CreatePanel(_adOverlay.transform, "AdCard", GameTheme.Panel);
            UiFactory.SetRect(
                card.rectTransform,
                new Vector2(0.08f, 0.28f),
                new Vector2(0.92f, 0.72f),
                Vector2.zero,
                Vector2.zero);

            var forced = UiFactory.CreateText(
                card.transform,
                "Forced",
                "REWARDED AD",
                22,
                GameTheme.CtaOrange,
                FontStyle.Bold,
                TextAnchor.MiddleCenter);
            UiFactory.SetRect(forced.rectTransform, new Vector2(0.05f, 0.82f), new Vector2(0.95f, 0.95f), Vector2.zero, Vector2.zero);

            _adHeadline = UiFactory.CreateText(
                card.transform,
                "Headline",
                "",
                32,
                GameTheme.TextPrimary,
                FontStyle.Bold,
                TextAnchor.MiddleCenter);
            UiFactory.SetRect(_adHeadline.rectTransform, new Vector2(0.08f, 0.45f), new Vector2(0.92f, 0.8f), Vector2.zero, Vector2.zero);

            var track = UiFactory.CreatePanel(card.transform, "ProgressTrack", new Color(0.2f, 0.22f, 0.26f, 1f));
            UiFactory.SetRect(track.rectTransform, new Vector2(0.1f, 0.28f), new Vector2(0.9f, 0.36f), Vector2.zero, Vector2.zero);

            _adProgressFill = UiFactory.CreatePanel(track.transform, "Fill", GameTheme.ProgressFill);
            UiFactory.SetRect(_adProgressFill.rectTransform, new Vector2(0f, 0f), new Vector2(0f, 1f), Vector2.zero, Vector2.zero);

            _adTimer = UiFactory.CreateText(
                card.transform,
                "Timer",
                "Skip in 5…",
                24,
                GameTheme.TextMuted,
                FontStyle.Normal,
                TextAnchor.MiddleCenter);
            UiFactory.SetRect(_adTimer.rectTransform, new Vector2(0.1f, 0.1f), new Vector2(0.9f, 0.24f), Vector2.zero, Vector2.zero);
        }

        private void BuildOfflineOverlay(Transform root)
        {
            _offlineOverlay = UiFactory.CreatePanel(root, "OfflineOverlay", GameTheme.AdOverlay).gameObject;
            _offlineOverlay.SetActive(false);

            var card = UiFactory.CreatePanel(_offlineOverlay.transform, "Card", GameTheme.Panel);
            UiFactory.SetRect(
                card.rectTransform,
                new Vector2(0.1f, 0.34f),
                new Vector2(0.9f, 0.66f),
                Vector2.zero,
                Vector2.zero);

            var title = UiFactory.CreateText(
                card.transform,
                "Title",
                "WHILE YOU WERE AWAY",
                28,
                GameTheme.AccentLime,
                FontStyle.Bold,
                TextAnchor.MiddleCenter);
            UiFactory.SetRect(title.rectTransform, new Vector2(0.06f, 0.7f), new Vector2(0.94f, 0.9f), Vector2.zero, Vector2.zero);

            _offlineBody = UiFactory.CreateText(
                card.transform,
                "Body",
                "",
                26,
                GameTheme.TextPrimary,
                FontStyle.Normal,
                TextAnchor.MiddleCenter);
            UiFactory.SetRect(_offlineBody.rectTransform, new Vector2(0.08f, 0.32f), new Vector2(0.92f, 0.68f), Vector2.zero, Vector2.zero);

            var ok = UiFactory.CreateButton(card.transform, "Ok", GameTheme.CtaOrange);
            UiFactory.SetRect(ok.GetComponent<RectTransform>(), new Vector2(0.2f, 0.08f), new Vector2(0.8f, 0.26f), Vector2.zero, Vector2.zero);
            var okLabel = UiFactory.CreateText(ok.transform, "Label", "CLAIM", 28, Color.white, FontStyle.Bold);
            UiFactory.Stretch(okLabel.rectTransform);
            ok.onClick.AddListener(() => DismissOffline?.Invoke());
        }

        public void Refresh(GameState state, bool adPlaying)
        {
            _attention.text = NumberFormatter.Format(state.Attention) + " Attention";
            _stats.text = "Ads watched: " + state.TotalAdsWatched
                          + "   ·   Autoplay: " + NumberFormatter.Format(Economy.AutoplayPerSecond(state)) + "/s";

            _watchButton.interactable = !adPlaying;
            _watchImage.color = adPlaying ? GameTheme.CtaDisabled : GameTheme.CtaOrange;
            _watchLabel.text = adPlaying
                ? "WATCHING…"
                : "WATCH AD (" + Economy.AdDurationSeconds(state).ToString("0.0") + "s)";

            for (var i = 0; i < UpgradeCatalog.All.Length; i++)
            {
                var upgrade = UpgradeCatalog.All[i];
                var level = state.GetLevel(upgrade.Id);
                var maxed = level >= upgrade.MaxLevel;
                var cost = upgrade.CostForLevel(level);
                var canBuy = !adPlaying && !maxed && Economy.CanAfford(state, upgrade);

                _upgradeButtons[i].interactable = canBuy;
                _upgradeImages[i].color = canBuy ? new Color(0.16f, 0.22f, 0.18f, 1f) : GameTheme.Panel;
                _upgradeLabels[i].text = maxed
                    ? upgrade.Name + "  Lv MAX\n" + upgrade.Description
                    : upgrade.Name + "  Lv " + level
                      + "  ·  " + NumberFormatter.Format(cost) + "\n"
                      + upgrade.Description;
            }
        }

        public void SetStatus(string message)
        {
            _status.text = message;
        }

        public void ShowAd(string headline)
        {
            _adOverlay.SetActive(true);
            _adHeadline.text = headline;
            UpdateAdProgress(0f, "Serving creative…");
        }

        public void UpdateAdProgress(float normalized, string timerText)
        {
            normalized = Mathf.Clamp01(normalized);
            _adProgressFill.rectTransform.anchorMax = new Vector2(normalized, 1f);
            _adTimer.text = timerText;
        }

        public void HideAd()
        {
            _adOverlay.SetActive(false);
        }

        public void ShowOffline(double earned)
        {
            if (earned < 0.5d)
                return;

            _offlineBody.text = NumberFormatter.Format(earned)
                                + " Attention earned from background ads.\n(Cap: 8 hours. HR is watching.)";
            _offlineOverlay.SetActive(true);
        }

        public void HideOffline()
        {
            _offlineOverlay.SetActive(false);
        }
    }
}
