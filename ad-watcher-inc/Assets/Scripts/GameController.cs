using System;
using AdWatcherInc.Core;
using AdWatcherInc.UI;
using UnityEngine;

namespace AdWatcherInc
{
    public sealed class GameController : MonoBehaviour
    {
        private GameState _state;
        private GameHud _hud;
        private readonly System.Random _rng = new System.Random();

        private bool _adPlaying;
        private float _adElapsed;
        private float _adDuration;
        private float _saveTimer;
        private float _statusPulse;

        private void Start()
        {
            _state = SaveSystem.LoadOrCreate();
            var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            var offline = Economy.ApplyOfflineEarnings(_state, now);

            var canvas = UiFactory.CreateCanvas("AdWatcherCanvas");
            DontDestroyOnLoad(canvas.gameObject);

            _hud = new GameHud();
            _hud.Build(canvas.transform);
            _hud.WatchClicked += OnWatchClicked;
            _hud.UpgradeClicked += OnUpgradeClicked;
            _hud.DismissOffline += () => _hud.HideOffline();

            _hud.Refresh(_state, false);
            _hud.ShowOffline(offline);
            _hud.SetStatus("Welcome back, Associate. Quota resets never.");
            SaveSystem.Save(_state);
        }

        private void Update()
        {
            var dt = Time.deltaTime;

            if (_adPlaying)
            {
                _adElapsed += dt;
                var t = Mathf.Clamp01(_adElapsed / _adDuration);
                var remaining = Mathf.Max(0f, _adDuration - _adElapsed);
                _hud.UpdateAdProgress(t, remaining > 0.05f
                    ? "Skip unavailable · " + remaining.ToString("0.0") + "s"
                    : "Claiming reward…");

                if (_adElapsed >= _adDuration)
                    CompleteAd();
            }
            else
            {
                var passive = Economy.AutoplayPerSecond(_state) * dt;
                if (passive > 0d)
                {
                    Economy.GrantAttention(_state, passive);
                    _statusPulse += dt;
                    if (_statusPulse > 1.5f)
                    {
                        _statusPulse = 0f;
                        _hud.SetStatus("Autoplay served another impression.");
                    }
                }
            }

            _saveTimer += dt;
            if (_saveTimer >= 2f)
            {
                _saveTimer = 0f;
                SaveSystem.Save(_state);
            }

            _hud.Refresh(_state, _adPlaying);
        }

        private void OnApplicationPause(bool pauseStatus)
        {
            if (pauseStatus)
                SaveSystem.Save(_state);
        }

        private void OnApplicationQuit()
        {
            SaveSystem.Save(_state);
        }

        private void OnWatchClicked()
        {
            if (_adPlaying)
                return;

            _adPlaying = true;
            _adElapsed = 0f;
            _adDuration = (float)Economy.AdDurationSeconds(_state);
            var headline = FakeAdCopy.NextHeadline(_rng);
            _state.LastAdHeadline = headline;
            _hud.ShowAd(headline);
            _hud.SetStatus("Optimizing your experience…");
        }

        private void CompleteAd()
        {
            _adPlaying = false;
            _hud.HideAd();

            var reward = Economy.RewardPerAd(_state);
            Economy.GrantAttention(_state, reward);
            _state.TotalAdsWatched += Math.Max(1, 1 + _state.GetLevel(UpgradeId.ParallelStreams));
            _hud.SetStatus("+" + NumberFormatter.Format(reward) + " Attention. Engagement looks strong.");
            SaveSystem.Save(_state);
            _hud.Refresh(_state, false);
        }

        private void OnUpgradeClicked(UpgradeId id)
        {
            if (_adPlaying)
                return;

            var upgrade = UpgradeCatalog.Get(id);
            if (!Economy.TryBuy(_state, upgrade))
            {
                _hud.SetStatus("Insufficient Attention. Watch more ads.");
                return;
            }

            _hud.SetStatus("Purchased " + upgrade.Name + ". Synergy increased.");
            SaveSystem.Save(_state);
            _hud.Refresh(_state, false);
        }
    }
}
