# AD WATCHER INC.

An idle / tap / upgrade game where **watching ads is the core loop** — a satire of mobile rewarded-video culture.

This folder is a **Unity 6** project (portrait mobile). A browser preview mirrors the MVP so you can feel the loop without waiting on an Editor install.

## Open in Unity (Windows)

1. Install [Unity Hub](https://unity.com/download) and **Unity 6 LTS** (matches `ProjectSettings/ProjectVersion.txt`).
2. Hub → **Add** → select this `ad-watcher-inc` folder  
   *(If Hub complains about packages, create a new **2D** Unity 6 project and copy `Assets/Scripts` + `Assets/Scenes` into it.)*
3. Open `Assets/Scenes/Main.unity` and press **Play**.
4. UI is built at runtime — you do not need to wire Canvas objects by hand.

`GameBootstrap` auto-spawns the game after scene load.

## What’s in the MVP

| Feature | Details |
|--------|---------|
| Core loop | Tap **WATCH AD** → fake interstitial timer → earn **Attention** |
| Upgrades | Shorter Skip Timer, Autoplay, Better CPM, Multi-Stream |
| Save / load | JSON under `Application.persistentDataPath` |
| Offline | Background Attention while away (8h cap) + claim modal |
| Juice | Overlay ad theater, progress bar, status quips, accent motion in web preview |

Real AdMob / IAP are **not** wired yet — fake ads only. Add Unity IAP + rewarded ads after the economy feels sticky.

## Browser preview

```bash
# from repo root
cd ad-watcher-inc/WebPreview
python -m http.server 8765
# open http://localhost:8765
```

Progress saves in `localStorage`.

## Project layout

```
ad-watcher-inc/
  Assets/
    Scenes/Main.unity
    Scripts/
      GameBootstrap.cs
      GameController.cs
      Core/          # economy, save, fake ad copy
      UI/            # runtime HUD
  WebPreview/        # same MVP in the browser
  Packages/
  ProjectSettings/
```

## Roadmap (store + monetization)

1. Polish juice (SFX, haptics, number pop)
2. Prestige (“Promotion to Ad Ops”)
3. **Unity IAP** — remove-ads / starter pack / cosmetics
4. **Rewarded ads** (optional 2×) via LevelPlay or AdMob
5. iOS export → Xcode on Mac/CI → TestFlight → App Store

iOS builds still require a Mac (or cloud Mac / Codemagic) for Xcode signing, even when you develop on Windows.

## Resetting save (Editor)

Delete:

`%USERPROFILE%\AppData\LocalLow\AdWatcherInc\Ad Watcher Inc\ad_watcher_save.json`

(Exact path appears in the Unity Console via `Application.persistentDataPath`.)
