import io
import math
import os
import random
import socket
import struct
import sys
import tkinter as tk
from tkinter import ttk
import wave
import winsound
from PIL import Image, ImageGrab, ImageSequence, ImageTk


def resource_path(relative_path: str) -> str:
    """Resolves asset paths for both normal script runs and PyInstaller --onefile builds."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_candidate = os.path.abspath(os.path.join(base_dir, "..", relative_path))
    if os.path.exists(parent_candidate):
        return parent_candidate
    return os.path.abspath(os.path.join(base_dir, relative_path))


class ZafkielAudio:
    """Synthesizes zero-dependency WAV sound effects in RAM for winsound."""

    def __init__(self, sample_rate: int = 22050):
        self.sr = sample_rate
        self.sounds = {
            "tick": self._build_tick(freq=1350, decay=45, duration=0.055),
            "tock": self._build_tick(freq=980, decay=45, duration=0.055),
            "clone": self._build_chime(),
            "error": self._build_error_chord(),
            "glitch": self._build_glitch(duration=0.22),
            "alarm": self._build_alarm(duration=0.45),
        }

    def _pack_wav(self, samples: list[int]) -> bytes:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sr)
            wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))
        return buf.getvalue()

    def _build_tick(self, freq: float, decay: float, duration: float) -> bytes:
        total = int(self.sr * duration)
        samples = []
        for i in range(total):
            t = i / self.sr
            env = math.exp(-decay * t)
            val = math.sin(2 * math.pi * freq * t) * env * 18000
            samples.append(int(max(-32767, min(32767, val))))
        return self._pack_wav(samples)

    def _build_chime(self) -> bytes:
        total = int(self.sr * 0.13)
        samples = []
        for i in range(total):
            t = i / self.sr
            freq = 740 + (950 * t * 6)
            env = math.exp(-18 * t)
            val = math.sin(2 * math.pi * freq * t) * env * 16000
            samples.append(int(max(-32767, min(32767, val))))
        return self._pack_wav(samples)

    def _build_error_chord(self) -> bytes:
        total = int(self.sr * 0.14)
        samples = []
        for i in range(total):
            t = i / self.sr
            env = math.exp(-14 * t)
            # Dissonant low Windows-style alert chord (190 Hz + 265 Hz)
            s1 = math.sin(2 * math.pi * 190 * t)
            s2 = 1.0 if math.sin(2 * math.pi * 265 * t) >= 0 else -1.0
            val = ((s1 * 0.6) + (s2 * 0.4)) * env * 17500
            samples.append(int(max(-32767, min(32767, val))))
        return self._pack_wav(samples)

    def _build_glitch(self, duration: float) -> bytes:
        total = int(self.sr * duration)
        samples = []
        hold = 0
        for i in range(total):
            if i % 18 == 0:
                hold = random.randint(-19000, 19000)
            t = i / self.sr
            mod = 1.0 if int(t * 60) % 2 == 0 else 0.3
            samples.append(int(hold * mod))
        return self._pack_wav(samples)

    def _build_alarm(self, duration: float) -> bytes:
        total = int(self.sr * duration)
        samples = []
        for i in range(total):
            t = i / self.sr
            freq = 145 - (55 * t)
            wave_val = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            env = math.exp(-3.5 * t)
            samples.append(int(wave_val * env * 20000))
        return self._pack_wav(samples)

    def play(self, name: str):
        data = self.sounds.get(name)
        if not data:
            return
        try:
            winsound.PlaySound(data, winsound.SND_MEMORY | winsound.SND_ASYNC)
        except Exception:
            pass


class KurumiFinalNightmare:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.audio = ZafkielAudio()
        self.hover_count = 0
        self.clones_spawned = False
        self.gif_after_id = None
        self.desktop_shot = None
        self.tile_refs = []
        self.error_popups = []

        self.victim_user = self._get_username()
        self.victim_host = socket.gethostname()
        self.cpu_threads = os.cpu_count() or 4

        self.gif_path = resource_path(os.path.join("assets", "tokisaki-kurumi.gif"))

        # Global emergency kill switch across all windows and widgets
        self.root.bind_all("<Escape>", lambda e: self.root.destroy())

        self.load_gif_frames()
        self.spawn_stage_one()
        self.root.mainloop()

    @staticmethod
    def _get_username() -> str:
        try:
            return os.getlogin()
        except Exception:
            return os.environ.get("USERNAME", "Shido-san")

    def load_gif_frames(self):
        self.frames = []
        try:
            img = Image.open(self.gif_path)
            self.frames = [
                ImageTk.PhotoImage(f.copy().convert("RGBA"))
                for f in ImageSequence.Iterator(img)
            ]
        except Exception:
            self.frames = []

    # =========================================================
    # STAGE 1: THE TIME TRAP & SHADOW CLONE CHAOS
    # =========================================================
    def spawn_stage_one(self):
        self.win = tk.Toplevel(self.root)
        self.win.title("Definitely No Suspicious Spirit")
        self.win.geometry("490x320")

        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        self.win.geometry(f"+{(sw - 490) // 2}+{(sh - 320) // 2}")

        self.win.configure(bg="#0d0d0d")
        self.win.attributes("-topmost", True)
        self.win.protocol("WM_DELETE_WINDOW", self.troll_close_button)

        self.taunt_label = tk.Label(
            self.win,
            text=f"\"Ara, ara~ Welcome, {self.victim_user}.\nZafkiel is hungry for your time~\"",
            fg="#ff4d6d",
            bg="#0d0d0d",
            font=("Consolas", 11, "bold"),
            wraplength=440,
        )
        self.taunt_label.pack(pady=24)

        self.btn_stop = tk.Button(
            self.win,
            text="   Th-thanks   ",
            bg="#3d0011",
            fg="white",
            activebackground="#66001a",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            command=self.try_trigger_stage_two,
        )
        self.btn_stop.place(x=190, y=155)
        self.btn_stop.bind("<Enter>", self.handle_hover)

    def troll_close_button(self):
        self.audio.play("alarm")
        self.taunt_label.config(
            text=f"\"Did you really think the X button would work, {self.victim_user}?\nHow cute~ (Press ESC if you surrender)\""
        )

    def handle_hover(self, event):
        self.hover_count += 1
        taunts = [
            f"\"Too slow, {self.victim_user}~ Your reflexes are tragic.\"",
            "\"Ara, ara~ Trying to escape Zafkiel?\"",
            "\"Kihihi~ Missed again!\"",
            "\"Eighth Bullet: Het! Which one is the real me?\"",
        ]
        if self.hover_count <= len(taunts):
            self.taunt_label.config(text=taunts[self.hover_count - 1])

        self.audio.play("tick" if self.hover_count % 2 == 0 else "tock")
        event.widget.place(x=random.randint(25, 355), y=random.randint(105, 260))

        if self.hover_count == 4 and not self.clones_spawned:
            self.clones_spawned = True
            self.audio.play("clone")
            for _ in range(5):
                self.spawn_clone_button()

    def spawn_clone_button(self):
        clone = tk.Button(
            self.win,
            text="   Th-thanks   ",
            bg="#3d0011",
            fg="white",
            font=("Segoe UI", 10, "bold"),
        )
        clone.place(x=random.randint(25, 355), y=random.randint(105, 260))
        clone.bind("<Enter>", self.handle_hover)
        clone.config(command=lambda b=clone: self.punish_fake_click(b))

    def punish_fake_click(self, btn):
        self.audio.play("clone")
        btn.config(text="Kihihi~ Fake!", bg="#7a0022")
        self.spawn_clone_button()

    def try_trigger_stage_two(self):
        if self.hover_count >= 4:
            self.start_desktop_shatter()

    # =========================================================
    # STAGE 2A: LIVE DESKTOP SCREENSHOT SHATTER
    # =========================================================
    def start_desktop_shatter(self):
        self.win.destroy()
        self.root.update_idletasks()

        try:
            self.desktop_shot = ImageGrab.grab(all_screens=True)
        except Exception:
            try:
                self.desktop_shot = ImageGrab.grab()
            except Exception:
                self.desktop_shot = None

        self.fs = tk.Toplevel(self.root)
        self.fs.overrideredirect(True)
        self.fs.attributes("-topmost", True)

        self.vx = self.fs.winfo_vrootx()
        self.vy = self.fs.winfo_vrooty()
        self.vw = self.fs.winfo_vrootwidth()
        self.vh = self.fs.winfo_vrootheight()

        self.fs.geometry(f"{self.vw}x{self.vh}+{self.vx}+{self.vy}")
        self.fs.configure(bg="black", cursor="none")

        if self.desktop_shot is None:
            self.start_collapse_ui()
            return

        self.audio.play("glitch")
        shot = self.desktop_shot.resize((self.vw, self.vh), Image.Resampling.NEAREST)

        self.canvas = tk.Canvas(
            self.fs, width=self.vw, height=self.vh, bg="black", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        cols, rows = 10, 6
        tile_w = self.vw // cols
        tile_h = self.vh // rows
        tiles = []
        self.tile_refs.clear()

        for r in range(rows):
            for c in range(cols):
                x1 = c * tile_w
                y1 = r * tile_h
                x2 = self.vw if c == cols - 1 else (c + 1) * tile_w
                y2 = self.vh if r == rows - 1 else (r + 1) * tile_h

                crop = shot.crop((x1, y1, x2, y2))
                tk_tile = ImageTk.PhotoImage(crop)
                self.tile_refs.append(tk_tile)

                item_id = self.canvas.create_image(x1, y1, anchor="nw", image=tk_tile)
                tiles.append(
                    {
                        "id": item_id,
                        "x": x1,
                        "y": y1,
                        "dx": random.uniform(-6, 6),
                        "dy": random.uniform(4, 14),
                        "delay": random.randint(0, 10),
                    }
                )

        def animate_shatter(step=0):
            active = False
            for t in tiles:
                if t["y"] > self.vh + 100:
                    continue
                active = True
                if step >= t["delay"]:
                    t["dy"] += 3.4
                    t["x"] += t["dx"]
                    t["y"] += t["dy"]
                    self.canvas.move(t["id"], t["dx"], t["dy"])

            if step in (7, 16):
                self.audio.play("glitch")

            if active and step < 42:
                self.root.after(24, lambda: animate_shatter(step + 1))
            else:
                self.canvas.destroy()
                self.tile_refs.clear()
                self.desktop_shot = None
                self.start_collapse_ui()

        animate_shatter(0)

    # =========================================================
    # STAGE 2B: CITY OF DEVOURING TIME (FAKE SYSTEM ROAST)
    # =========================================================
    def start_collapse_ui(self):
        primary_w = self.fs.winfo_screenwidth()
        primary_h = self.fs.winfo_screenheight()
        panel_w, panel_h = 640, 470
        self.base_x = -self.vx + (primary_w - panel_w) // 2
        self.base_y = -self.vy + (primary_h - panel_h) // 2

        self.center_frame = tk.Frame(self.fs, bg="black")
        self.center_frame.place(x=self.base_x, y=self.base_y, width=panel_w, height=panel_h)

        if self.frames:
            self.gif_label = tk.Label(self.center_frame, bg="black")
            self.gif_label.pack(pady=8)
            self.animate_gif(self.gif_label, 0)

        spec_text = (
            f"TARGET: {self.victim_user}@{self.victim_host}  |  "
            f"CPU: {self.cpu_threads} Threads  |  STATUS: COMPROMISED"
        )
        tk.Label(
            self.center_frame,
            text=spec_text,
            fg="#ff8099",
            bg="#1a0007",
            font=("Consolas", 9, "bold"),
            padx=10,
            pady=5,
        ).pack(pady=6)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Red.Horizontal.TProgressbar",
            troughcolor="#1a0000",
            background="#cc0022",
            thickness=22,
        )

        self.progress = ttk.Progressbar(
            self.center_frame,
            length=540,
            mode="determinate",
            style="Red.Horizontal.TProgressbar",
        )
        self.progress.pack(pady=10)

        self.log_label = tk.Label(
            self.center_frame,
            text="ZAFKIEL PROTOCOL: 0%",
            fg="#ff1a40",
            bg="black",
            font=("Consolas", 15, "bold"),
        )
        self.log_label.pack(pady=4)

        self.roast_label = tk.Label(
            self.center_frame,
            text="Initializing City of Devouring Time...",
            fg="#cccccc",
            bg="black",
            font=("Consolas", 11),
            wraplength=580,
        )
        self.roast_label.pack(pady=4)

        self.toast_label = tk.Label(
            self.center_frame,
            text="[Discord Auto-Broadcast] Queuing Camera_Roll_Backup.zip...",
            fg="#ff4d6d",
            bg="#141519",
            font=("Consolas", 9),
            padx=12,
            pady=6,
        )
        self.toast_label.pack(pady=10)

        self.run_fake_deletion()

    def animate_gif(self, label, counter):
        if not self.frames or not label.winfo_exists():
            return
        label.configure(image=self.frames[counter])
        self.gif_after_id = self.root.after(
            85, lambda: self.animate_gif(label, (counter + 1) % len(self.frames))
        )

    def run_fake_deletion(self):
        fake_logs = [
            f"Scanning C:\\Users\\{self.victim_user}\\Desktop\\Homework_Folder (68.4 GB)... oh my~",
            "Extracting browser_incognito_history.db...",
            "Searching for 'touching_grass.exe'... 0 results found.",
            "Draining remaining lifespan via Zafkiel: Aleph!",
            "CRITICAL: Reality anchor failing at 99%...",
        ]
        toast_logs = [
            "[Discord Auto-Broadcast] Uploading Camera_Roll_Backup.zip (34%)...",
            "[Discord Auto-Broadcast] Sending Incognito_History.txt to @everyone...",
            "[Discord Auto-Broadcast] Packaging Reaction_Screenshot.png (88%)...",
            "[Discord Auto-Broadcast] Finalizing transfer to public channels...",
        ]

        def step(p):
            if p <= 100:
                self.progress["value"] = p
                self.log_label.config(text=f"CORRUPTING REALITY: {p}%")

                tick_interval = 10 if p < 55 else (5 if p < 85 else 2)
                if p % tick_interval == 0:
                    self.audio.play("tick" if (p // tick_interval) % 2 == 0 else "tock")

                if p % 20 == 0 and p < 100:
                    idx = (p // 20) - 1
                    self.roast_label.config(text=fake_logs[idx])
                    self.toast_label.config(text=toast_logs[min(idx, len(toast_logs) - 1)])

                if p == 99:
                    self.roast_label.config(text=fake_logs[-1], fg="#ff3355")
                    self.audio.play("alarm")
                    self.shake_screen(22, lambda: self.root.after(300, lambda: step(100)))
                    return

                # Fine-tuned pacing: brisk build-up, tense slowdown near 99%
                delay = 36 if p < 75 else 54
                self.root.after(delay, lambda: step(p + 1))
            else:
                self.trigger_error_cascade()

        step(0)

    def shake_screen(self, count, on_done):
        if count <= 0:
            self.center_frame.place(x=self.base_x, y=self.base_y)
            on_done()
            return
        dx = random.randint(-15, 15)
        dy = random.randint(-15, 15)
        self.center_frame.place(x=self.base_x + dx, y=self.base_y + dy)
        self.root.after(35, lambda: self.shake_screen(count - 1, on_done))

    # =========================================================
    # STAGE 2C: FAKE WINDOWS ERROR POPUP CASCADE
    # =========================================================
    def trigger_error_cascade(self):
        error_messages = [
            ("ZAFKIEL.EXE - Application Error", "The instruction at 0x00000000 referenced memory at 0xZAFKIEL."),
            ("System Integrity Warning", "Critical file C:\\Windows\\System32\\hal.dll was devoured."),
            ("Windows Security Alert", "Threat 'Kurumi.Nightmare.Gen' blocked user action 'Escape'."),
            ("Kernel Time Drift", "Hardware clock desynchronized by -50 years."),
            ("FATAL EXCEPTION", "Reality anchor stopped working. Preparing emergency dump..."),
        ]

        primary_w = self.fs.winfo_screenwidth()
        primary_h = self.fs.winfo_screenheight()
        total_popups = 15

        def spawn_popup(idx):
            if idx >= total_popups:
                self.root.after(380, self.trigger_bsod)
                return

            title, body = error_messages[idx % len(error_messages)]
            pop = tk.Toplevel(self.fs)
            pop.overrideredirect(True)
            pop.attributes("-topmost", True)
            pop.configure(bg="#1f1f1f", highlightbackground="#ff2a55", highlightthickness=1)

            w, h = 360, 135
            # Mix diagonal cascade with chaotic scatter across primary screen
            if idx < 7:
                px = 140 + (idx * 42)
                py = 110 + (idx * 34)
            else:
                px = random.randint(60, max(100, primary_w - w - 60))
                py = random.randint(60, max(100, primary_h - h - 60))

            pop.geometry(f"{w}x{h}+{px}+{py}")

            # Title bar
            bar = tk.Frame(pop, bg="#66001a", height=26)
            bar.pack(fill="x")
            tk.Label(
                bar, text=f"  {title}", fg="white", bg="#66001a", font=("Segoe UI", 9, "bold")
            ).pack(side="left", pady=2)
            tk.Label(
                bar, text="✕  ", fg="#ff99aa", bg="#66001a", font=("Segoe UI", 9, "bold")
            ).pack(side="right", pady=2)

            # Content row with red X icon
            content = tk.Frame(pop, bg="#1f1f1f")
            content.pack(fill="both", expand=True, padx=14, pady=10)

            icon = tk.Canvas(content, width=32, height=32, bg="#1f1f1f", highlightthickness=0)
            icon.pack(side="left", padx=(0, 12))
            icon.create_oval(2, 2, 30, 30, fill="#d92638", outline="")
            icon.create_line(10, 10, 22, 22, fill="white", width=3)
            icon.create_line(22, 10, 10, 22, fill="white", width=3)

            tk.Label(
                content,
                text=body,
                fg="#f0f0f0",
                bg="#1f1f1f",
                font=("Segoe UI", 9),
                justify="left",
                wraplength=275,
            ).pack(side="left", fill="both")

            # Fake OK button
            tk.Label(
                pop,
                text="   OK   ",
                fg="white",
                bg="#333333",
                font=("Segoe UI", 8, "bold"),
                pady=3,
            ).pack(side="bottom", pady=(0, 8))

            self.error_popups.append(pop)
            self.audio.play("error")

            # Accelerate spawn rate as cascade builds
            next_delay = max(45, 95 - (idx * 4))
            self.root.after(next_delay, lambda: spawn_popup(idx + 1))

        spawn_popup(0)

    # =========================================================
    # STAGE 3: WINDOWS BSOD -> CRIMSON ZAFKIEL OVERRIDE
    # =========================================================
    def trigger_bsod(self):
        for pop in self.error_popups:
            try:
                pop.destroy()
            except Exception:
                pass
        self.error_popups.clear()

        if self.gif_after_id:
            self.root.after_cancel(self.gif_after_id)
            self.gif_after_id = None

        self.center_frame.destroy()
        self.audio.play("glitch")

        def flicker(n):
            if n > 0:
                self.fs.configure(bg=random.choice(["#0078d7", "black", "#66001a"]))
                self.root.after(45, lambda: flicker(n - 1))
            else:
                start_blue_screen()

        def start_blue_screen():
            self.fs.configure(bg="#0078d7")
            left_x = -self.vx + int(self.fs.winfo_screenwidth() * 0.12)
            top_y = -self.vy + int(self.fs.winfo_screenheight() * 0.16)

            self.bsod_face = tk.Label(
                self.fs, text=":(", fg="white", bg="#0078d7", font=("Segoe UI", 85)
            )
            self.bsod_face.place(x=left_x, y=top_y)

            self.bsod_lbl = tk.Label(
                self.fs,
                text="",
                fg="white",
                bg="#0078d7",
                font=("Segoe UI", 20),
                justify="left",
                wraplength=920,
            )
            self.bsod_lbl.place(x=left_x, y=top_y + 165)
            update_bsod(0)

        def update_bsod(p):
            if p <= 100:
                if p == 40:
                    self.audio.play("alarm")

                if p >= 40:
                    bg_color = "#590016"
                    self.fs.configure(bg=bg_color)
                    self.bsod_face.config(text=">:3", bg=bg_color)
                    self.bsod_lbl.config(bg=bg_color)
                    msg = (
                        f"ZAFKIEL OVERRIDE: Your time now belongs to Kurumi Tokisaki, {self.victim_user}.\n\n"
                        f"{p}% complete\n\n"
                        "Stop code: SPIRIT_TIME_LEAK_0xZAFKIEL"
                    )
                else:
                    msg = (
                        "Your PC ran into a problem and needs to restart.\n\n"
                        f"{p}% complete\n\n"
                        "Stop code: CRITICAL_PROCESS_DIED"
                    )

                self.bsod_lbl.config(text=msg)
                self.root.after(65, lambda: update_bsod(p + 2))
            else:
                self.show_thank_you_screen()

        flicker(8)

    # =========================================================
    # STAGE 4: CINEMATIC FADE-IN REVEAL
    # =========================================================
    def show_thank_you_screen(self):
        for widget in self.fs.winfo_children():
            widget.destroy()

        self.fs.configure(bg="black", cursor="arrow")
        self.fs.attributes("-alpha", 0.0)

        thanks_frame = tk.Frame(self.fs, bg="black")
        thanks_frame.place(x=self.base_x, y=self.base_y, width=640, height=470)

        if self.frames:
            final_gif = tk.Label(thanks_frame, bg="black")
            final_gif.pack(pady=8)
            self.animate_gif(final_gif, 0)

        tk.Label(
            thanks_frame,
            text="ARA ARA~!",
            fg="#ff4d6d",
            bg="black",
            font=("Consolas", 42, "bold"),
        ).pack()

        tk.Label(
            thanks_frame,
            text="Thanks for trying out Project Nightmare!\nNo files, photos, or system settings were actually harmed.",
            fg="white",
            bg="black",
            font=("Segoe UI", 14),
        ).pack(pady=14)

        tk.Button(
            thanks_frame,
            text="Exit Simulation",
            bg="#ff3366",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            padx=22,
            pady=8,
            relief="flat",
            command=self.root.destroy,
        ).pack(pady=8)

        def fade(alpha):
            if alpha <= 1.0:
                self.fs.attributes("-alpha", alpha)
                self.root.after(35, lambda: fade(alpha + 0.05))

        fade(0.0)


if __name__ == "__main__":
    KurumiFinalNightmare()