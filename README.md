<div align="center">

# 🕰️ Project Nightmare

> *"Ara, ara~ Zafkiel is hungry for your time..."*

[![Live Demo](https://img.shields.io/badge/Live_Web_Prank-GitHub_Pages-ff1a40?style=for-the-badge&logo=github)](https://zrayce.github.io/Project-Nightmare/)
[![Windows EXE](https://img.shields.io/badge/Download-SystemVerify.exe-800020?style=for-the-badge&logo=windows)](https://github.com/ZRayce/Project-Nightmare/releases)
[![Python](https://img.shields.io/badge/Python-3.10%2B-ffd700?style=for-the-badge&logo=python&logoColor=black)](#desktop-setup--standalone-exe)
[![Safety](https://img.shields.io/badge/100%25_Harmless-Visual_Illusion-10b981?style=for-the-badge)](#%EF%B8%8F-disclaimer)

A multi-platform **Kurumi Tokisaki** (*Date A Live*) psychological prank simulation featuring unsuspecting parody bait links for PC and mobile, stereo Web Audio / WAV synthesis, and a native Windows `Melt.exe` desktop illusion engine.

</div>

---

## 🌐 Live Web Prank Links

> **PC and mobile** · Hosted with GitHub Pages · OpenGraph preview cards · Fullscreen re-sync · Refresh persistence · Stereo panning audio

| Disguise theme | Live bait URL | Preview card |
|:---|:---|:---|
| 🚀 **ChatterBox Nitro** | [nitrosaurus.html](https://zrayce.github.io/Project-Nightmare/nitrosaurus.html) | 1-Month Nitro Boost & HD Streaming Gift |
| 🎬 **StreamFlix 4K** | [streamflix.html](https://zrayce.github.io/Project-Nightmare/streamflix.html) | Ultra HD Family Profile Slot Invite |
| ☁️ **CloudVault** | [clouddrive.html](https://zrayce.github.io/Project-Nightmare/clouddrive.html) | Shared Backup Folder (24 Items) |
| 📦 **QuickDrop Express** | [parceltrack.html](https://zrayce.github.io/Project-Nightmare/parceltrack.html) | Delivery Attempt Paused Action Notice |
| 🎮 **SteamVault** | [gamevault.html](https://zrayce.github.io/Project-Nightmare/gamevault.html) | Redeemable Digital Wallet & Game Key |
| ✨ **VIP Pro Pass** | [trial.html](https://zrayce.github.io/Project-Nightmare/trial.html) | 30-Day Free Trial Activation Pass |

### 🔗 Custom URL Parameters

Customize any link above with query parameters, or generate one directly on the final reveal screen:

| Parameter | Description |
|:---|:---|
| `?to=Name` | Kurumi addresses the target by name across popups, hardware scans, and fake wipe logs. |
| `?from=YourName` | Credits you on the final reveal screen. |
| `?demand=500_Headpats` | Replaces the `$9,999.00 USD` ransomware demand with a custom currency or amount. |
| `?skip=1` | **Instant Ambush Mode:** skips the Stage 1 button chase and immediately triggers the UAC prompt. |

**Example:**

```text
https://zrayce.github.io/Project-Nightmare/nitrosaurus.html?to=Shido&from=Rayce&skip=1
```

---

## 🎬 The Zafkiel Experience

### Fast Time Trap & Eighth Bullet (Het)

A taunting popup dodges twice before splitting into shadow clones. Clicking any button, or hesitating for 2.5 seconds, triggers the next stage.

### UAC / Root Permission Hijack

Spoofs a Windows User Account Control prompt (`ZafkielKernelHost.exe`) or a mobile root dialog that shakes and appears to accept itself.

### Desktop Melt.exe & City of Devouring Time

- **Windows Desktop:** Captures an in-memory screenshot and melts it downward in 56 vertical wave strips.
- **Reality Collapse:** Spins a Roman numeral Zafkiel clock behind local hardware callouts (CPU threads, GPU, timezone), a DSLR camera shutter flash, Windows USB disconnect alerts, a 47-viewer live stream chat, and a Windows Defender “Threat blocked failed” toast.

### Fourth Bullet (Dalet)

Rewinds the deletion progress bar from 99% back to 45% before slamming it to 100%.

### Sticky Notes & Error Cascade

Spawns yellow sticky notes forming a `>:3` face alongside a spoofed Task Manager (99.8% CPU) and cascading error dialogs.

### 1:1 BSOD, Seventh Bullet (Zayin) & Twelfth Bullet (Yud Bet)

Hijacks a Windows Blue Screen into a crimson RGB-glitched override (`0xZAFKIEL`), pauses for a monochrome Zayin time-freeze, flashes a Windows 98 56k dial-up box, and cycles through an AMIBIOS S.M.A.R.T. STATUS BAD POST screen and hijacked Windows boot logo.

### Accelerated Ransomware, Ghost Cursor & CRT Turn-Off

Features a `02:00` countdown accelerated by Aleph, possessed keyboard typing, magnetic cursor pull toward **Confirm Drive Format**, a fake `C:\` / `/storage` wipe cascade, a Double-Cross fake reveal, and a retro CRT TV turn-off into the final reveal.

---

## 📂 Repository Structure

```text
Project-Nightmare/
├── .github/
│   └── workflows/
│       └── build-exe.yml        # Automated PyInstaller Windows .exe release builder
├── assets/
│   └── tokisaki-kurumi.gif      # Shared visual asset (converted to kurumi.ico on build)
├── Python-Version/
│   ├── kurumi_sim.py            # Desktop Melt.exe, stereo WAV SFX & Zafkiel BSOD engine
│   ├── make_icon.py             # Generates a multi-size Windows .ico from the GIF
│   └── requirements.txt         # Minimal dependencies (Pillow)
├── index.html                   # Core web prank engine (PC and mobile responsive)
├── nitrosaurus.html             # Parody chat Nitro gift wrapper
├── streamflix.html              # Parody 4K streaming invite wrapper
├── clouddrive.html              # Parody cloud storage folder wrapper
├── parceltrack.html             # Parody express parcel tracking wrapper
├── gamevault.html               # Parody digital game key wrapper
├── trial.html                   # Parody 30-day VIP free trial wrapper
├── gift.html                    # Classic mystery gift wrapper
├── album.html                   # Classic shared photo album wrapper
├── .gitignore                   # Excludes build/, dist/, and local cache
└── README.md                    # Documentation
```

---

## 💻 Desktop Setup & Standalone Executable

### Download the Pre-Built Windows Executable

Grab the latest `SystemVerify.exe` directly from the [GitHub Releases page](https://github.com/ZRayce/Project-Nightmare/releases). It is automatically compiled with GitHub Actions and a custom Kurumi icon.

### Run from Source

Requires Python 3.10+ on Windows and Pillow:

```bash
pip install -r Python-Version/requirements.txt
python Python-Version/kurumi_sim.py
```

### Build a Single-File Windows `.exe` Locally

```bash
pip install pyinstaller pillow
python Python-Version/make_icon.py
pyinstaller --noconfirm --onefile --windowed --name "SystemVerify" --icon "assets/kurumi.ico" --add-data "assets/tokisaki-kurumi.gif;assets" Python-Version/kurumi_sim.py
```

---

## ⌨️ Emergency Override

- **ESC key:** Pressing Escape at any stage immediately terminates the simulation, restores the cursor, and jumps to the safe reveal screen.
- **Reset / Exit:** A reset and exit button appears automatically after the final reveal finishes fading in.

---

## ⚠️ Disclaimer

- **100% Harmless Illusion:** Project Nightmare is a visual and audio prank created purely for entertainment.
- **Zero System Changes:** No files, photos, registry keys, or system settings are modified, encrypted, or deleted.
- **Zero Data Collection:** No real webcam or microphone access is requested, and no data is transmitted over the network. In-memory screenshots and synthesized WAV audio exist only in RAM and vanish immediately on exit.

---

## 🕰️ A Tribute to the Worst Spirit

Dedicated to Kurumi Tokisaki (Nightmare) and the *Date A Live* universe.

Remember: never trust a mysterious gift link when the clock strikes XII, or Zafkiel might just borrow a few years of your lifespan~

*Crafted with crimson chaos by ZRayce.*