# 🕰️ Project Nightmare

> *"Ara, ara~ Zafkiel is hungry for your time..."*

A multi-platform **Kurumi Tokisaki** (*Date A Live*) psychological prank simulation featuring shareable mobile/PC web bait links and a native Windows desktop shatter engine.

---

## 🌐 Live Web Prank Links (PC & Mobile)

Host via **GitHub Pages** to prank friends with a single tap—complete with device fullscreen lock, Web Audio clock ticks, phone vibration, local GPU/battery hardware callouts, and a blue-to-crimson Zafkiel BSOD:

* **Direct Simulation:** `https://zrayce.github.io/Project-Nightmare/`
* **Mystery Gift Disguise:** `https://zrayce.github.io/Project-Nightmare/gift.html`
* **Shared Photo Album Disguise:** `https://zrayce.github.io/Project-Nightmare/album.html`

> **Personalize the target:** Append `?to=FriendName` to any link above (e.g., `.../gift.html?to=Shido`) so Kurumi addresses them by name throughout the trap.

---

## 📂 Repository Structure

```text
Project-Nightmare/
├── .github/
│   └── workflows/
│       └── build-exe.yml        # Automated PyInstaller Windows .exe builder
├── assets/
│   └── tokisaki-kurumi.gif      # Shared visual asset across Web & Desktop
├── Python-Version/
│   ├── kurumi_sim.py            # Desktop shatter, error cascade & Zafkiel BSOD
│   └── requirements.txt         # Minimal dependencies (Pillow)
├── index.html                   # Core Web prank engine (PC & Mobile)
├── gift.html                    # OpenGraph preview wrapper ("Mystery Gift")
├── album.html                   # OpenGraph preview wrapper ("Shared Album")
├── .gitignore                   # Excludes build artifacts and local cache
└── README.md                    # Documentation
```

---

## 🎬 The Experience

**1. The Time Trap & Eighth Bullet (Het):** A suspicious popup taunts the user with a button that dodges their cursor/thumb. On the 4th dodge, Kurumi splits the button into **shadow clones**, clicking a fake spawns even more.

**2. Live Desktop Shatter (Python):** Captures an in-memory screenshot of the user's actual desktop and shatters their icons into black void under gravity.

**3. City of Devouring Time:** Displays real local hardware specs (username, CPU threads, GPU/battery) while running a fake file roast, simulated Discord broadcast toast, and a dramatic **99% stall with screen shake.**

**4. Error Cascade & Zafkiel BSOD:** Rapidly cascades Windows error popups before hijacking a realistic Windows Blue Screen into a crimson **Zafkiel Override** (0xZAFKIEL).

**5. The Restoration:** Smoothly fades into the final reveal screen with a custom link builder on the web version.

---

## Desktop Setup & Standalone .exe
Run from Source (Python)
Requires Python 3.10+ on Windows and Pillow:

```Bash
pip install -r Python-Version/requirements.txt
python Python-Version/kurumi_sim.py
```

---

## Build a Single-File Windows .exe
Compile kurumi_sim.py and assets/tokisaki-kurumi.gif into a standalone executable (dist/SystemVerify.exe) that runs on Windows PCs without Python installed:

```Bash
pip install pyinstaller pillow
pyinstaller --noconfirm --onefile --windowed --name "SystemVerify" --add-data "assets/tokisaki-kurumi.gif;assets" Python-Version/kurumi_sim.py
```

---

## ⌨️ Emergency Override

ESC Key: Pressing Escape at any stage immediately terminates the simulation and restores your screen.

Exit / Reset Button: Appears automatically once the final reveal finishes fading in.

## ⚠️ Disclaimer

Project Nightmare is a harmless visual prank created purely for entertainment.

No files, photos, or system settings are modified, encrypted, or deleted.

No camera/microphone access is requested, and no data is ever transmitted over the network.

In-memory screenshots and synthesized WAV audio exist solely in RAM and vanish immediately on exit.


---

### 2. `.gitignore` & GitHub Actions Auto-Build Workflow

#### `.gitignore` (Root Folder)

```gitignore
# Python cache & virtual environments
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
env/

# PyInstaller build artifacts
build/
dist/
*.spec

# Editor & OS files
.vscode/
.idea/
.DS_Store
Thumbs.db
```