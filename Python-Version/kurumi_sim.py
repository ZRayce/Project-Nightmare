import datetime
import io
import math
import os
import random
import socket
import struct
import sys
import time
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
            "usb": self._build_usb_disconnect(),
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

    def _build_usb_disconnect(self) -> bytes:
        # Descending two-tone Windows USB unplug chime (D5 -> A4)
        total = int(self.sr * 0.22)
        half = total // 2
        samples = []
        for i in range(total):
            freq = 587.33 if i < half else 440.0
            local_t = (i % half) / self.sr
            env = math.exp(-14 * local_t)
            val = math.sin(2 * math.pi * freq * local_t) * env * 17000
            samples.append(int(max(-32767, min(32767, val))))
        return self._pack_wav(samples)

    def _build_error_chord(self) -> bytes:
        total = int(self.sr * 0.14)
        samples = []
        for i in range(total):
            t = i / self.sr
            env = math.exp(-14 * t)
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
        self.uac_triggered = False
        self.gif_after_id = None
        self.desktop_shot = None
        self.tile_refs = []
        self.error_popups = []
        self.tear_bars = []
        self.glitch_active = False
        self.ransom_active = False
        self.ghost_active = False
        self.ghost_win = None
        self.wipe_started = False
        self.possessed_idx = 0

        self.victim_user = self._get_username()
        self.victim_host = socket.gethostname()
        self.cpu_threads = os.cpu_count() or 4
        self.local_tz = time.tzname[0] if time.tzname else "UTC"

        self.gif_path = resource_path(os.path.join("assets", "tokisaki-kurumi.gif"))

        # Global emergency kill switch across all windows and widgets
        self.root.bind_all("<Escape>", lambda e: self.cleanup_and_exit())

        self.load_gif_frames()
        self.spawn_stage_one()
        self.root.mainloop()

    def cleanup_and_exit(self):
        self.stop_ghost_cursor()
        try:
            self.root.destroy()
        except Exception:
            pass

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
    # STAGE 1: FAST 2-DODGE TIME TRAP (2.5s AUTO-DETONATION)
    # =========================================================
    def spawn_stage_one(self):
        self.win = tk.Toplevel(self.root)
        self.win.title("Definitely No Suspicious Spirit")
        self.win.geometry("490x310")

        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        self.win.geometry(f"+{(sw - 490) // 2}+{(sh - 310) // 2}")

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
            command=self.start_uac_trap,
        )
        self.btn_stop.place(x=190, y=155)
        self.btn_stop.bind("<Enter>", self.handle_hover)

        # Auto-detonate after 2.5 seconds if user freezes
        self.root.after(2500, lambda: self.start_uac_trap() if self.win.winfo_exists() else None)

    def troll_close_button(self):
        self.audio.play("alarm")
        self.taunt_label.config(
            text=f"\"Did you really think the X button would work, {self.victim_user}?\nHow cute~ (Press ESC to surrender)\""
        )

    def handle_hover(self, event):
        self.hover_count += 1
        self.audio.play("tick" if self.hover_count % 2 == 0 else "tock")
        event.widget.place(x=random.randint(25, 355), y=random.randint(105, 250))

        if self.hover_count == 1:
            self.taunt_label.config(text=f"\"Too slow, {self.victim_user}~\"")
        elif self.hover_count == 2 and not self.clones_spawned:
            self.clones_spawned = True
            self.taunt_label.config(text="\"Eighth Bullet: Het! Nowhere to run~\"")
            self.audio.play("clone")
            for _ in range(4):
                self.spawn_clone_button()
        elif self.hover_count >= 3:
            self.start_uac_trap()

    def spawn_clone_button(self):
        clone = tk.Button(
            self.win,
            text="   Th-thanks   ",
            bg="#3d0011",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.start_uac_trap,
        )
        clone.place(x=random.randint(25, 355), y=random.randint(105, 250))
        clone.bind("<Enter>", self.handle_hover)

    # =========================================================
    # STAGE 1.5: FAKE WINDOWS UAC PROMPT THAT AUTO-CLICKS "YES"
    # =========================================================
    def start_uac_trap(self):
        if hasattr(self, "fs") and self.fs.winfo_exists():
            return
        if self.win.winfo_exists():
            self.win.destroy()
        self.root.update_idletasks()

        self.fs = tk.Toplevel(self.root)
        self.fs.overrideredirect(True)
        self.fs.attributes("-topmost", True)

        self.vx = self.fs.winfo_vrootx()
        self.vy = self.fs.winfo_vrooty()
        self.vw = self.fs.winfo_vrootwidth()
        self.vh = self.fs.winfo_vrootheight()

        self.fs.geometry(f"{self.vw}x{self.vh}+{self.vx}+{self.vy}")
        self.fs.configure(bg="#05060a")

        primary_w = self.fs.winfo_screenwidth()
        primary_h = self.fs.winfo_screenheight()
        mw, mh = 460, 290
        mx = -self.vx + (primary_w - mw) // 2
        my = -self.vy + (primary_h - mh) // 2

        modal = tk.Frame(self.fs, bg="#1f1f1f", highlightbackground="#4a4a4a", highlightthickness=1)
        modal.place(x=mx, y=my, width=mw, height=mh)

        top_bar = tk.Frame(modal, bg="#005a9e", height=74)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        shield = tk.Canvas(top_bar, width=36, height=36, bg="#005a9e", highlightthickness=0)
        shield.pack(side="left", padx=(18, 12), pady=18)
        shield.create_polygon(18, 3, 32, 8, 32, 19, 18, 33, 4, 19, 4, 8, fill="#ffd43b", outline="white", width=1)
        shield.create_polygon(18, 3, 32, 8, 32, 19, 18, 33, fill="#339af0", outline="")

        tk.Label(
            top_bar,
            text="Do you want to allow this app from an unknown\npublisher to make changes to your device?",
            fg="white",
            bg="#005a9e",
            font=("Segoe UI", 10, "bold"),
            justify="left",
        ).pack(side="left", pady=14)

        body = tk.Frame(modal, bg="#1f1f1f")
        body.pack(fill="both", expand=True, padx=20, pady=14)

        tk.Label(body, text="ZafkielKernelHost.exe", fg="white", bg="#1f1f1f", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(
            body,
            text="Publisher: Unknown\nFile origin: Hard drive on this computer\nProgram location: \"C:\\Windows\\Temp\\ZafkielKernelHost.exe\"",
            fg="#cccccc",
            bg="#1f1f1f",
            font=("Segoe UI", 9),
            justify="left",
        ).pack(anchor="w", pady=(6, 4))

        status_lbl = tk.Label(body, text="", fg="#ff4d6d", bg="#1f1f1f", font=("Consolas", 9, "bold"))
        status_lbl.pack(anchor="w", pady=(6, 0))

        btn_row = tk.Frame(modal, bg="#1f1f1f")
        btn_row.pack(fill="x", padx=20, pady=(0, 18))

        def override_uac(clicked_yes=False):
            if self.uac_triggered:
                return
            self.uac_triggered = True

            if not clicked_yes:
                self.audio.play("error")
                no_btn.config(state="disabled", bg="#262626")
                status_lbl.config(text="\"Did I ask for permission? Overriding to YES...\"")
                modal.place(x=mx - 10, y=my + 4)
                self.root.after(70, lambda: modal.place(x=mx + 10, y=my - 4))
                self.root.after(140, lambda: modal.place(x=mx, y=my))
                self.root.after(240, lambda: yes_btn.config(bg="#0078d7"))
            else:
                yes_btn.config(bg="#0078d7")
                status_lbl.config(text="Elevating privileges to NT AUTHORITY\\SYSTEM...")

            self.root.after(760, self.start_desktop_vortex)

        yes_btn = tk.Button(
            btn_row, text="Yes", bg="#333333", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", pady=6,
            command=lambda: override_uac(True),
        )
        yes_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        no_btn = tk.Button(
            btn_row, text="No", bg="#333333", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", pady=6,
            command=lambda: override_uac(False),
        )
        no_btn.pack(side="left", fill="x", expand=True, padx=(6, 0))

        self.audio.play("tick")
        self.root.after(2400, lambda: override_uac(False))

    # =========================================================
    # STAGE 2A: LIVE DESKTOP BLACK-HOLE SPIRAL VORTEX
    # =========================================================
    def start_desktop_vortex(self):
        for w in self.fs.winfo_children():
            w.destroy()

        self.fs.configure(bg="black", cursor="none")
        self.fs.withdraw()
        self.root.update()

        try:
            self.desktop_shot = ImageGrab.grab(all_screens=True)
        except Exception:
            try:
                self.desktop_shot = ImageGrab.grab()
            except Exception:
                self.desktop_shot = None

        self.fs.deiconify()

        if self.desktop_shot is None:
            self.start_collapse_ui()
            return

        self.audio.play("glitch")
        shot = self.desktop_shot.resize((self.vw, self.vh), Image.Resampling.NEAREST)

        self.canvas = tk.Canvas(
            self.fs, width=self.vw, height=self.vh, bg="black", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        cx = self.vw / 2.0
        cy = self.vh / 2.0
        cols, rows = 8, 6
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

                tx = x1 + (x2 - x1) / 2.0
                ty = y1 + (y2 - y1) / 2.0
                radius = math.hypot(tx - cx, ty - cy)
                angle = math.atan2(ty - cy, tx - cx)

                item_id = self.canvas.create_image(tx, ty, anchor="center", image=tk_tile)
                tiles.append(
                    {
                        "id": item_id,
                        "radius": radius,
                        "angle": angle,
                        "spin": random.uniform(0.11, 0.19),
                    }
                )

        def animate_vortex(step=0):
            if step < 34:
                for t in tiles:
                    t["angle"] += t["spin"]
                    t["radius"] *= 0.89
                    nx = cx + t["radius"] * math.cos(t["angle"])
                    ny = cy + t["radius"] * math.sin(t["angle"])
                    self.canvas.coords(t["id"], nx, ny)

                if step in (8, 18):
                    self.audio.play("glitch")
                self.root.after(24, lambda: animate_vortex(step + 1))
            else:
                self.canvas.destroy()
                self.tile_refs.clear()
                self.desktop_shot = None
                self.start_collapse_ui()

        animate_vortex(0)

    # =========================================================
    # STAGE 2B: CITY OF DEVOURING TIME + ZAFKIEL CLOCK + DALET REWIND
    # =========================================================
    def start_collapse_ui(self):
        primary_w = self.fs.winfo_screenwidth()
        primary_h = self.fs.winfo_screenheight()
        panel_w, panel_h = 640, 470
        self.base_x = -self.vx + (primary_w - panel_w) // 2
        self.base_y = -self.vy + (primary_h - panel_h) // 2

        px0 = -self.vx
        py0 = -self.vy

        # Spinning Roman Numeral Zafkiel Clock Canvas behind UI
        self.clock_canvas = tk.Canvas(
            self.fs, width=primary_w, height=primary_h, bg="black", highlightthickness=0
        )
        self.clock_canvas.place(x=px0, y=py0)

        self.clock_running = [True]
        self.clock_dir = [1]
        romans = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]

        def draw_zafkiel_clock(deg=0):
            if not self.clock_running[0] or not self.clock_canvas.winfo_exists():
                return
            self.clock_canvas.delete("all")
            ccx, ccy = primary_w // 2, primary_h // 2
            r_outer = min(primary_w, primary_h) // 2 - 35
            r_inner = int(r_outer * 0.78)

            self.clock_canvas.create_oval(
                ccx - r_outer, ccy - r_outer, ccx + r_outer, ccy + r_outer,
                outline="#59450e", width=3
            )
            self.clock_canvas.create_oval(
                ccx - r_inner, ccy - r_inner, ccx + r_inner, ccy + r_inner,
                outline="#4d0013", width=2, dash=(6, 4)
            )
            for idx, num in enumerate(romans):
                a = math.radians(deg + idx * 30 - 90)
                nx = ccx + (r_outer - 22) * math.cos(a)
                ny = ccy + (r_outer - 22) * math.sin(a)
                self.clock_canvas.create_text(
                    nx, ny, text=num, fill="#7a5e14", font=("Times New Roman", 16, "bold")
                )

            # Clock hands
            ha = math.radians(deg * 2.5)
            self.clock_canvas.create_line(
                ccx, ccy, ccx + (r_inner - 20) * math.cos(ha), ccy + (r_inner - 20) * math.sin(ha),
                fill="#800020", width=4
            )
            self.root.after(45, lambda: draw_zafkiel_clock((deg + 2 * self.clock_dir[0]) % 360))

        draw_zafkiel_clock(0)

        # Glowing red screen-share border & pill
        self.live_borders = [
            tk.Frame(self.fs, bg="#ff1a40", height=4, width=primary_w),
            tk.Frame(self.fs, bg="#ff1a40", height=4, width=primary_w),
            tk.Frame(self.fs, bg="#ff1a40", height=primary_h, width=4),
            tk.Frame(self.fs, bg="#ff1a40", height=primary_h, width=4),
        ]
        self.live_borders[0].place(x=px0, y=py0)
        self.live_borders[1].place(x=px0, y=py0 + primary_h - 4)
        self.live_borders[2].place(x=px0, y=py0)
        self.live_borders[3].place(x=px0 + primary_w - 4, y=py0)

        self.live_pill = tk.Label(
            self.fs,
            text="  ● LIVE — Sharing Screen to Public Channel (47 viewers)  ",
            fg="white",
            bg="#1a0006",
            highlightbackground="#ff2a55",
            highlightthickness=1,
            font=("Segoe UI", 9, "bold"),
            pady=4,
        )
        self.live_pill.place(x=px0 + (primary_w - 360) // 2, y=py0 + 10, width=360)

        self.center_frame = tk.Frame(self.fs, bg="black")
        self.center_frame.place(x=self.base_x, y=self.base_y, width=panel_w, height=panel_h)

        if self.frames:
            self.gif_label = tk.Label(self.center_frame, bg="black")
            self.gif_label.pack(pady=8)
            self.animate_gif(self.gif_label, 0)

        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        yud_roast = (
            f"Up at {time_str}? How unhealthy~"
            if 0 <= now.hour <= 4
            else f"Time: {time_str} ({self.local_tz})"
        )
        spec_text = (
            f"TARGET: {self.victim_user}@{self.victim_host}  |  "
            f"YUD: {yud_roast}  |  CPU: {self.cpu_threads}T"
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

        self.spawn_defender_toast(px0, py0, primary_w, primary_h)
        self.root.after(1100, lambda: self.flash_camera_shutter(px0, py0, primary_w, primary_h))
        self.root.after(1750, lambda: self.spawn_usb_toast(px0, py0, "Keyboard & Mouse input disconnected"))
        self.root.after(2400, lambda: self.spawn_dm_toast(px0, py0, primary_w, primary_h))

        self.run_fake_deletion(px0, py0)

    def flash_camera_shutter(self, px0, py0, primary_w, primary_h):
        if not self.fs.winfo_exists():
            return
        flash = tk.Frame(self.fs, bg="white")
        flash.place(x=px0, y=py0, width=primary_w, height=primary_h)
        self.audio.play("glitch")
        self.root.after(120, flash.destroy)

    def spawn_usb_toast(self, px0, py0, msg: str):
        if not self.fs.winfo_exists():
            return
        self.audio.play("usb")
        box = tk.Frame(self.fs, bg="#1b1d23", highlightbackground="#ff9900", highlightthickness=1)
        box.place(x=px0 + 18, y=py0 + 52, width=300, height=54)
        tk.Label(
            box,
            text=f"🔌 USB Device Unplugged\n{msg}",
            fg="white",
            bg="#1b1d23",
            font=("Segoe UI", 9, "bold"),
            justify="left",
            anchor="w",
            padx=10,
        ).pack(fill="both", expand=True)
        self.root.after(1450, box.destroy)

    def spawn_dm_toast(self, px0, py0, primary_w, primary_h):
        if not self.fs.winfo_exists():
            return
        self.audio.play("clone")
        dm = tk.Frame(self.fs, bg="#2b2d31", highlightbackground="#5865F2", highlightthickness=1)
        dm.place(x=px0 + primary_w - 370, y=py0 + primary_h - 215, width=350, height=62)
        tk.Label(
            dm,
            text=f"💬 Group Chat • Discord\nbro {self.victim_user} why did you just send that?? 😭💀",
            fg="#f2f3f5",
            bg="#2b2d31",
            font=("Segoe UI", 9, "bold"),
            justify="left",
            anchor="w",
            padx=10,
        ).pack(fill="both", expand=True)

    def spawn_defender_toast(self, px0, py0, primary_w, primary_h):
        tw, th = 350, 96
        target_x = px0 + primary_w - tw - 20
        start_x = px0 + primary_w + 10
        ty = py0 + primary_h - th - 45

        self.def_toast = tk.Frame(
            self.fs, bg="#1e1e1e", highlightbackground="#e81123", highlightthickness=1
        )
        self.def_toast.place(x=start_x, y=ty, width=tw, height=th)

        accent = tk.Frame(self.def_toast, bg="#e81123", width=5)
        accent.pack(side="left", fill="y")

        inner = tk.Frame(self.def_toast, bg="#1e1e1e")
        inner.pack(side="left", fill="both", expand=True, padx=10, pady=8)

        tk.Label(
            inner, text="🛡️ Windows Security  •  Just now",
            fg="white", bg="#1e1e1e", font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill="x")
        tk.Label(
            inner, text="Threat blocked failed",
            fg="#ff4d6d", bg="#1e1e1e", font=("Segoe UI", 10, "bold"), anchor="w"
        ).pack(fill="x", pady=(2, 1))
        tk.Label(
            inner,
            text="Severe: Ransom:Win32/Zafkiel.A!ml\nRemediation incomplete (Access denied by SYSTEM)",
            fg="#cccccc", bg="#1e1e1e", font=("Segoe UI", 8), justify="left", anchor="w"
        ).pack(fill="x")

        def slide_in(curr_x):
            if not self.def_toast.winfo_exists():
                return
            if curr_x > target_x:
                nxt = max(target_x, curr_x - 28)
                self.def_toast.place(x=nxt, y=ty)
                self.root.after(18, lambda: slide_in(nxt))
            else:
                self.audio.play("error")

        self.root.after(450, lambda: slide_in(start_x))

    def animate_gif(self, label, counter):
        if not self.frames or not label.winfo_exists():
            return
        label.configure(image=self.frames[counter])
        self.gif_after_id = self.root.after(
            85, lambda: self.animate_gif(label, (counter + 1) % len(self.frames))
        )

    def run_fake_deletion(self, px0, py0):
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

        dalet_done = [False]

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

                # FOURTH BULLET: DALET (Rewind from 99% back to 45% once)
                if p == 99 and not dalet_done[0]:
                    dalet_done[0] = True
                    self.clock_dir[0] = -6
                    self.roast_label.config(
                        text="FOURTH BULLET: DALET! Let's enjoy that panic one more time~",
                        fg="#ffd700",
                    )
                    self.audio.play("clone")

                    def resume_after_rewind():
                        self.clock_dir[0] = 2
                        self.roast_label.config(fg="#cccccc")
                        step(45)

                    self.root.after(750, resume_after_rewind)
                    return

                if p == 99 and dalet_done[0]:
                    self.roast_label.config(text=fake_logs[-1], fg="#ff3355")
                    self.spawn_usb_toast(px0, py0, "Primary Drive C:\\ disconnected")
                    self.shake_screen(18, lambda: self.root.after(240, lambda: step(100)))
                    return

                delay = 28 if not dalet_done[0] else 16
                self.root.after(delay, lambda: step(p + 1))
            else:
                self.clock_running[0] = False
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
    # STAGE 2C: ERROR POPUP CASCADE + SPOOFED TASK MANAGER
    # =========================================================
    def spawn_fake_task_manager(self):
        primary_w = self.fs.winfo_screenwidth()
        primary_h = self.fs.winfo_screenheight()
        tm = tk.Toplevel(self.fs)
        tm.overrideredirect(True)
        tm.attributes("-topmost", True)
        tm.configure(bg="#181818", highlightbackground="#555555", highlightthickness=1)

        tw, th = 370, 145
        tx = primary_w - tw - random.randint(24, 90)
        ty = primary_h - th - random.randint(24, 90)
        tm.geometry(f"{tw}x{th}+{tx}+{ty}")

        bar = tk.Frame(tm, bg="#2b2b2b", height=24)
        bar.pack(fill="x")
        tk.Label(bar, text="  Task Manager — Processes", fg="white", bg="#2b2b2b", font=("Segoe UI", 9, "bold")).pack(side="left")

        row = tk.Frame(tm, bg="#181818")
        row.pack(fill="x", padx=12, pady=12)
        tk.Label(row, text="ZafkielKernelHost.exe (32 bit)", fg="#ff4d6d", bg="#181818", font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(row, text="99.8% CPU", fg="#ff4d6d", bg="#181818", font=("Segoe UI", 9, "bold")).pack(side="right")

        end_btn = tk.Button(
            tm,
            text="End Task",
            bg="#66001a",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=12,
            command=lambda: (self.audio.play("error"), end_btn.config(text="Access Denied (Cloned!)"), self.spawn_fake_task_manager()),
        )
        end_btn.pack(side="right", padx=12, pady=(0, 10))
        self.error_popups.append(tm)

    def trigger_error_cascade(self):
        self.spawn_fake_task_manager()

        error_messages = [
            ("ZAFKIEL.EXE - Application Error", "The instruction at 0x00000000 referenced memory at 0xZAFKIEL."),
            ("System Integrity Warning", "Critical file C:\\Windows\\System32\\hal.dll was devoured."),
            ("Windows Security Alert", "Threat 'Kurumi.Nightmare.Gen' blocked user action 'Escape'."),
            ("Kernel Time Drift", "Hardware clock desynchronized by -50 years."),
            ("FATAL EXCEPTION", "Reality anchor stopped working. Preparing emergency dump..."),
        ]

        primary_w = self.fs.winfo_screenwidth()
        primary_h = self.fs.winfo_screenheight()
        total_popups = 12

        def spawn_popup(idx):
            if idx >= total_popups:
                self.root.after(320, self.trigger_bsod)
                return

            title, body = error_messages[idx % len(error_messages)]
            pop = tk.Toplevel(self.fs)
            pop.overrideredirect(True)
            pop.attributes("-topmost", True)
            pop.configure(bg="#1f1f1f", highlightbackground="#ff2a55", highlightthickness=1)

            w, h = 360, 135
            if idx < 5:
                px = 140 + (idx * 42)
                py = 110 + (idx * 34)
            else:
                px = random.randint(60, max(100, primary_w - w - 60))
                py = random.randint(60, max(100, primary_h - h - 60))

            pop.geometry(f"{w}x{h}+{px}+{py}")

            bar = tk.Frame(pop, bg="#66001a", height=26)
            bar.pack(fill="x")
            tk.Label(bar, text=f"  {title}", fg="white", bg="#66001a", font=("Segoe UI", 9, "bold")).pack(side="left", pady=2)
            tk.Label(bar, text="✕  ", fg="#ff99aa", bg="#66001a", font=("Segoe UI", 9, "bold")).pack(side="right", pady=2)

            content = tk.Frame(pop, bg="#1f1f1f")
            content.pack(fill="both", expand=True, padx=14, pady=10)

            icon = tk.Canvas(content, width=32, height=32, bg="#1f1f1f", highlightthickness=0)
            icon.pack(side="left", padx=(0, 12))
            icon.create_oval(2, 2, 30, 30, fill="#d92638", outline="")
            icon.create_line(10, 10, 22, 22, fill="white", width=3)
            icon.create_line(22, 10, 10, 22, fill="white", width=3)

            tk.Label(
                content, text=body, fg="#f0f0f0", bg="#1f1f1f",
                font=("Segoe UI", 9), justify="left", wraplength=275
            ).pack(side="left", fill="both")

            tk.Label(
                pop, text="   OK   ", fg="white", bg="#333333",
                font=("Segoe UI", 8, "bold"), pady=3
            ).pack(side="bottom", pady=(0, 8))

            self.error_popups.append(pop)
            self.audio.play("error")

            next_delay = max(45, 90 - (idx * 4))
            self.root.after(next_delay, lambda: spawn_popup(idx + 1))

        spawn_popup(0)

    # =========================================================
    # STAGE 3: WINDOWS BSOD + RGB GLITCH + ZAYIN FREEZE + WIN98 FLASH
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

        for w in self.fs.winfo_children():
            w.destroy()

        self.audio.play("glitch")
        win_blue = "#0078d7"
        self.fs.configure(bg=win_blue)

        left_x = -self.vx + int(self.fs.winfo_screenwidth() * 0.12)
        top_y = -self.vy + int(self.fs.winfo_screenheight() * 0.15)

        self.face_cyan = tk.Label(self.fs, text=":(", fg="#00f0ff", bg=win_blue, font=("Segoe UI Light", 88))
        self.face_red = tk.Label(self.fs, text=":(", fg="#ff003c", bg=win_blue, font=("Segoe UI Light", 88))
        self.bsod_face = tk.Label(self.fs, text=":(", fg="white", bg=win_blue, font=("Segoe UI Light", 88))

        self.lbl_cyan = tk.Label(self.fs, text="", fg="#00f0ff", bg=win_blue, font=("Segoe UI Light", 21), justify="left", wraplength=920)
        self.lbl_red = tk.Label(self.fs, text="", fg="#ff003c", bg=win_blue, font=("Segoe UI Light", 21), justify="left", wraplength=920)
        self.bsod_lbl = tk.Label(self.fs, text="", fg="white", bg=win_blue, font=("Segoe UI Light", 21), justify="left", wraplength=920)

        self.bsod_face.place(x=left_x, y=top_y)
        self.bsod_lbl.place(x=left_x, y=top_y + 170)

        def run_rgb_glitch():
            if not self.glitch_active or not self.fs.winfo_exists():
                return

            for bar in self.tear_bars:
                try:
                    bar.destroy()
                except Exception:
                    pass
            self.tear_bars.clear()

            bg_choice = random.choice(["#590016", "#590016", "#000000", "#1a0008"])
            self.fs.configure(bg=bg_choice)

            cx, cy = random.randint(-18, -5), random.randint(-6, 6)
            rx, ry = random.randint(5, 18), random.randint(-6, 6)
            mx, my = random.randint(-8, 8), random.randint(-4, 4)

            for w in (self.face_cyan, self.face_red, self.bsod_face, self.lbl_cyan, self.lbl_red, self.bsod_lbl):
                w.config(bg=bg_choice)

            self.face_cyan.place(x=left_x + cx, y=top_y + cy)
            self.face_red.place(x=left_x + rx, y=top_y + ry)
            self.bsod_face.place(x=left_x + mx, y=top_y + my)

            self.lbl_cyan.place(x=left_x + cx, y=top_y + 170 + cy)
            self.lbl_red.place(x=left_x + rx, y=top_y + 170 + ry)
            self.bsod_lbl.place(x=left_x + mx, y=top_y + 170 + my)

            for _ in range(7):
                tear = tk.Frame(
                    self.fs,
                    bg=random.choice(["#00f0ff", "#ff003c", "#ffffff", "#000000"]),
                    height=random.randint(3, 16),
                    width=self.vw,
                )
                tear.place(x=random.randint(-40, 40), y=random.randint(0, self.vh))
                self.tear_bars.append(tear)

            self.root.after(55, run_rgb_glitch)

        zayin_done = [False]
        yud_bet_done = [False]

        def update_bsod(p):
            if p <= 100:
                if p == 32:
                    self.audio.play("glitch")
                    self.glitch_active = True
                    run_rgb_glitch()

                # SEVENTH BULLET: ZAYIN (Dead-silent monochrome time freeze at 58%)
                if p == 58 and not zayin_done[0]:
                    zayin_done[0] = True
                    self.glitch_active = False
                    for bar in self.tear_bars:
                        try:
                            bar.destroy()
                        except Exception:
                            pass
                    self.tear_bars.clear()

                    self.fs.configure(bg="#1c1c1c")
                    for w in (self.face_cyan, self.face_red, self.lbl_cyan, self.lbl_red):
                        w.place_forget()
                    self.bsod_face.config(bg="#1c1c1c", fg="#e0e0e0")
                    self.bsod_lbl.config(bg="#1c1c1c", fg="#e0e0e0")

                    banner = tk.Label(
                        self.fs,
                        text="  SEVENTH BULLET: ZAYIN — TIME FROZEN  ",
                        fg="white",
                        bg="black",
                        highlightbackground="white",
                        highlightthickness=2,
                        font=("Consolas", 16, "bold"),
                        pady=10,
                    )
                    banner.place(x=self.base_x + 60, y=self.base_y + 190)

                    def unfreeze():
                        banner.destroy()
                        self.bsod_face.config(fg="white")
                        self.bsod_lbl.config(fg="white")
                        self.glitch_active = True
                        run_rgb_glitch()
                        update_bsod(p + 2)

                    self.root.after(1450, unfreeze)
                    return

                # TWELFTH BULLET: YUD BET (Retro Windows 98 flash at 82%)
                if p == 82 and not yud_bet_done[0]:
                    yud_bet_done[0] = True
                    self.audio.play("alarm")
                    w98 = tk.Frame(self.fs, bg="#c0c0c0", highlightbackground="white", highlightthickness=2)
                    w98.place(x=self.base_x + 120, y=self.base_y + 140, width=400, height=140)
                    tk.Label(w98, text="  Zafkiel_1998.exe — Illegal Operation", fg="white", bg="#000080", font=("Consolas", 9, "bold"), anchor="w").pack(fill="x")
                    tk.Label(
                        w98,
                        text="TWELFTH BULLET: YUD BET!\nOS reverted to Windows 98. Dialing 56k leak server...",
                        fg="black", bg="#c0c0c0", font=("Consolas", 9), justify="left", padx=12, pady=16
                    ).pack(fill="both")
                    self.root.after(620, w98.destroy)

                if p > 34 and p % 16 == 0:
                    self.audio.play("glitch")

                if p >= 32:
                    face_txt = ">:3"
                    msg = (
                        f"ZAFKIEL OVERRIDE: Your PC now belongs to Kurumi Tokisaki, {self.victim_user}.\n\n"
                        f"{p}% complete\n\n"
                        "Stop code: SPIRIT_TIME_LEAK_0xZAFKIEL"
                    )
                else:
                    face_txt = ":("
                    msg = (
                        "Your PC ran into a problem and needs to restart. We're just\n"
                        "collecting some error info, and then we'll restart for you.\n\n"
                        f"{p}% complete\n\n"
                        "Stop code: CRITICAL_PROCESS_DIED"
                    )

                for f_lbl in (self.face_cyan, self.face_red, self.bsod_face):
                    f_lbl.config(text=face_txt)
                for b_lbl in (self.lbl_cyan, self.lbl_red, self.bsod_lbl):
                    b_lbl.config(text=msg)

                self.root.after(60, lambda: update_bsod(p + 2))
            else:
                self.glitch_active = False
                for bar in self.tear_bars:
                    try:
                        bar.destroy()
                    except Exception:
                        pass
                self.tear_bars.clear()
                self.start_bios_post()

        update_bsod(0)

    # =========================================================
    # STAGE 4: AMERICAN MEGATRENDS BIOS POST SCREEN
    # =========================================================
    def start_bios_post(self):
        for widget in self.fs.winfo_children():
            widget.destroy()

        self.fs.configure(bg="black")
        left_x = -self.vx + 36
        top_y = -self.vy + 32

        header = tk.Frame(self.fs, bg="black")
        header.place(x=left_x, y=top_y)

        tri = tk.Canvas(header, width=38, height=34, bg="black", highlightthickness=0)
        tri.pack(side="left", padx=(0, 12))
        tri.create_polygon(19, 2, 36, 32, 2, 32, fill="#d92638", outline="")
        tri.create_polygon(19, 12, 27, 27, 11, 27, fill="black", outline="")

        tk.Label(
            header,
            text="AMIBIOS(C) 2026 American Megatrends, Inc.\nBIOS Date: 11/26/2026 Ver: 08.00.15-ZAFKIEL",
            fg="#e0e0e0",
            bg="black",
            font=("Consolas", 12, "bold"),
            justify="left",
        ).pack(side="left")

        lines_frame = tk.Frame(self.fs, bg="black")
        lines_frame.place(x=left_x, y=top_y + 56)

        bios_entries = [
            (f"CPU : {self.cpu_threads}-Core Processor @ 4.20 GHz", "#cccccc", False),
            ("Memory Test : 16384MB OK", "#cccccc", False),
            ("Detecting Primary Master ... NVMe SSD 1024GB", "#cccccc", False),
            ("PRI MASTER DISK: S.M.A.R.T. STATUS BAD — BACKUP AND REPLACE", "#ff3355", True),
            ("FATAL: Master Boot Record overwritten by 0xZAFKIEL", "#ff3355", True),
            ("Booting into emergency lock environment...", "#cccccc", False),
        ]

        def show_bios_line(idx=0):
            if idx < len(bios_entries):
                txt, col, bold = bios_entries[idx]
                tk.Label(
                    lines_frame,
                    text=txt,
                    fg=col,
                    bg="black",
                    font=("Consolas", 12, "bold" if bold else "normal"),
                    anchor="w",
                ).pack(fill="x", pady=2)
                self.audio.play("error" if bold else "tick")
                self.root.after(320, lambda: show_bios_line(idx + 1))
            else:
                self.root.after(600, self.start_fake_boot)

        show_bios_line(0)

    # =========================================================
    # STAGE 5: FAKE WINDOWS BOOT SCREEN
    # =========================================================
    def start_fake_boot(self):
        for widget in self.fs.winfo_children():
            widget.destroy()

        self.fs.configure(bg="black")
        boot_frame = tk.Frame(self.fs, bg="black")
        boot_frame.place(x=self.base_x, y=self.base_y, width=640, height=470)

        logo_canvas = tk.Canvas(boot_frame, width=100, height=100, bg="black", highlightthickness=0)
        logo_canvas.pack(pady=(55, 45))
        panes = [
            logo_canvas.create_rectangle(6, 6, 47, 47, fill="#0078d7", outline=""),
            logo_canvas.create_rectangle(53, 6, 94, 47, fill="#0078d7", outline=""),
            logo_canvas.create_rectangle(6, 53, 47, 94, fill="#0078d7", outline=""),
            logo_canvas.create_rectangle(53, 53, 94, 94, fill="#0078d7", outline=""),
        ]

        spin_canvas = tk.Canvas(boot_frame, width=64, height=64, bg="black", highlightthickness=0)
        spin_canvas.pack(pady=10)

        status_lbl = tk.Label(
            boot_frame,
            text="Restarting...",
            fg="#e0e0e0",
            bg="black",
            font=("Segoe UI Light", 16),
        )
        status_lbl.pack(pady=16)

        boot_running = [True]

        def animate_dots(angle=0):
            if not boot_running[0] or not spin_canvas.winfo_exists():
                return
            spin_canvas.delete("all")
            cx, cy, r = 32, 32, 20
            for i in range(5):
                a = math.radians(angle - (i * 26))
                x = cx + r * math.cos(a)
                y = cy + r * math.sin(a)
                spin_canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="white", outline="")
            self.root.after(30, lambda: animate_dots((angle + 11) % 360))

        animate_dots(0)

        self.root.after(1000, lambda: status_lbl.config(text="Preparing Automatic Repair..."))

        def hijack_boot():
            self.audio.play("glitch")
            for p_id in panes:
                logo_canvas.itemconfig(p_id, fill="#cc0022")
            status_lbl.config(text="CRITICAL: Boot sector hijacked by ZAFKIEL.EXE", fg="#ff3366")

        self.root.after(2000, hijack_boot)

        def finish_boot():
            boot_running[0] = False
            self.start_fake_ransomware()

        self.root.after(3100, finish_boot)

    # =========================================================
    # STAGE 6: RANSOMWARE + POSSESSED KEYBOARD + GHOST CURSOR
    # =========================================================
    def start_ghost_cursor(self, target_btn: tk.Widget):
        self.ghost_active = True
        self.fs.configure(cursor="none")

        key_color = "#010203"
        self.ghost_win = tk.Toplevel(self.fs)
        self.ghost_win.overrideredirect(True)
        self.ghost_win.attributes("-topmost", True)
        self.ghost_win.wm_attributes("-transparentcolor", key_color)
        self.ghost_win.configure(bg=key_color)

        c = tk.Canvas(self.ghost_win, width=28, height=28, bg=key_color, highlightthickness=0)
        c.pack()
        c.create_polygon(2, 2, 22, 14, 13, 16, 18, 24, 14, 26, 9, 18, 2, 23, fill="white", outline="#ff003c", width=2)

        gx = [self.fs.winfo_screenwidth() * 0.25]
        gy = [self.fs.winfo_screenheight() * 0.25]
        self.ghost_win.geometry(f"28x28+{int(gx[0])}+{int(gy[0])}")

        def drag_loop():
            if not self.ghost_active or not self.ghost_win or not self.ghost_win.winfo_exists():
                return
            try:
                tx = target_btn.winfo_rootx() + (target_btn.winfo_width() // 2)
                ty = target_btn.winfo_rooty() + (target_btn.winfo_height() // 2)

                mx, my = self.root.winfo_pointerxy()
                gx[0] = gx[0] * 0.84 + tx * 0.14 + (mx - gx[0]) * 0.02 + random.uniform(-3, 3)
                gy[0] = gy[0] * 0.84 + ty * 0.14 + (my - gy[0]) * 0.02 + random.uniform(-3, 3)

                self.ghost_win.geometry(f"28x28+{int(gx[0])}+{int(gy[0])}")

                if math.hypot(tx - gx[0], ty - gy[0]) < 32:
                    target_btn.config(bg="#ff0033")
            except Exception:
                pass
            self.root.after(28, drag_loop)

        drag_loop()

    def stop_ghost_cursor(self):
        self.ghost_active = False
        if self.ghost_win:
            try:
                self.ghost_win.destroy()
            except Exception:
                pass
            self.ghost_win = None

    def start_fake_ransomware(self):
        for widget in self.fs.winfo_children():
            widget.destroy()

        self.fs.configure(bg="#260008")
        self.ransom_active = True

        panel_w, panel_h = 740, 480
        rx = -self.vx + (self.fs.winfo_screenwidth() - panel_w) // 2
        ry = -self.vy + (self.fs.winfo_screenheight() - panel_h) // 2

        panel = tk.Frame(self.fs, bg="#140005", highlightbackground="#ff1a40", highlightthickness=2)
        panel.place(x=rx, y=ry, width=panel_w, height=panel_h)

        banner = tk.Frame(panel, bg="#99001f", height=40)
        banner.pack(fill="x")
        tk.Label(
            banner,
            text="  🔒 ZAFKIEL LOCKER v2.0 — WINDOWS C:\\ ENCRYPTED",
            fg="white",
            bg="#99001f",
            font=("Segoe UI", 11, "bold"),
        ).pack(side="left", pady=8)
        tk.Label(
            banner,
            text="AES-4096  ",
            fg="#ffccd5",
            bg="#99001f",
            font=("Consolas", 10, "bold"),
        ).pack(side="right", pady=8)

        body = tk.Frame(panel, bg="#140005")
        body.pack(fill="both", expand=True, padx=18, pady=16)

        left_col = tk.Frame(body, bg="#1f0008", highlightbackground="#590016", highlightthickness=1, width=215)
        left_col.pack(side="left", fill="y", padx=(0, 16))
        left_col.pack_propagate(False)

        tk.Label(left_col, text="FILES WILL BE WIPED IN", fg="#ff99ad", bg="#1f0008", font=("Segoe UI", 9, "bold")).pack(pady=(18, 4))
        timer_lbl = tk.Label(left_col, text="02:00", fg="#ff2a55", bg="#1f0008", font=("Consolas", 30, "bold"))
        timer_lbl.pack()
        taunt_lbl = tk.Label(left_col, text="Time is ticking~", fg="#cccccc", bg="#1f0008", font=("Segoe UI", 9))
        taunt_lbl.pack(pady=(2, 16))

        tk.Frame(left_col, bg="#4d0013", height=1).pack(fill="x", padx=14, pady=6)

        tk.Label(left_col, text="RANSOM DEMAND", fg="#ff99ad", bg="#1f0008", font=("Segoe UI", 9, "bold")).pack(pady=(12, 4))
        tk.Label(left_col, text="$9,999.00 USD", fg="white", bg="#1f0008", font=("Segoe UI", 15, "bold")).pack()
        tk.Label(left_col, text="or 50 Years of Lifespan", fg="#ff4d6d", bg="#1f0008", font=("Segoe UI", 9)).pack(pady=2)

        right_col = tk.Frame(body, bg="#140005")
        right_col.pack(side="left", fill="both", expand=True)

        note_box = tk.Frame(right_col, bg="#0d0003", highlightbackground="#4d0013", highlightthickness=1)
        note_box.pack(fill="both", expand=True)

        note_text = (
            f"Ooops, {self.victim_user}! Your PC files have been encrypted.\n\n"
            f"All documents, game saves, Desktop folders, and browser passwords on "
            f"C:\\Users\\{self.victim_user}\\ are sealed with .zafkiel extensions.\n\n"
            "Pay $9,999.00 USD (or surrender 50 years of lifespan) before the 02:00 "
            "timer hits zero, or every partition on your drive will be permanently wiped."
        )
        tk.Label(
            note_box,
            text=note_text,
            fg="#f2d9de",
            bg="#0d0003",
            font=("Segoe UI", 9.5),
            justify="left",
            wraplength=445,
            padx=14,
            pady=10,
        ).pack(anchor="nw")

        # Possessed keyboard entry box
        possessed_entry = tk.Entry(
            right_col,
            bg="#1a0007",
            fg="#ff8099",
            insertbackground="#ff2a55",
            font=("Consolas", 10, "bold"),
            relief="flat",
        )
        possessed_entry.pack(fill="x", pady=(8, 0), ipady=5)
        possessed_entry.insert(0, "Type decryption key here...")
        possessed_entry.bind("<FocusIn>", lambda e: possessed_entry.delete(0, "end") if "Type decryption" in possessed_entry.get() else None)

        phrase = "A R A  A R A  S A V E  M E  K U R U M I  "

        def on_possessed_key(event):
            if event.keysym == "Escape":
                self.cleanup_and_exit()
                return "break"
            if "Type decryption" in possessed_entry.get():
                possessed_entry.delete(0, "end")
            possessed_entry.insert("end", phrase[self.possessed_idx % len(phrase)])
            self.possessed_idx += 1
            self.audio.play("tick")
            return "break"

        possessed_entry.bind("<Key>", on_possessed_key)

        btn_row = tk.Frame(right_col, bg="#140005")
        btn_row.pack(fill="x", pady=(10, 0))

        pay_btn = tk.Button(
            btn_row,
            text="Verify Payment",
            bg="#cc0022",
            fg="white",
            font=("Segoe UI", 9.5, "bold"),
            relief="flat",
            pady=7,
            command=lambda: self.start_fake_wipe("Payment verification failed! Initiating immediate wipe..."),
        )
        pay_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        format_btn = tk.Button(
            btn_row,
            text="Confirm Drive Format",
            bg="#2b000a",
            fg="white",
            font=("Segoe UI", 9.5, "bold"),
            relief="flat",
            pady=7,
            command=lambda: self.start_fake_wipe("Drive format confirmed! Purging all partitions..."),
        )
        format_btn.pack(side="left", fill="x", expand=True, padx=4)

        status_line = tk.Label(
            right_col,
            text="⚠️ Mouse input hijacked — Cursor pulled toward Drive Format!",
            fg="#ff4d6d",
            bg="#140005",
            font=("Consolas", 8, "bold"),
            anchor="w",
        )
        status_line.pack(fill="x", pady=(6, 0))

        tk.Button(
            btn_row,
            text="Watch Ad (Save 1 Folder)",
            bg="#1e222d",
            fg="#a5b4fc",
            font=("Segoe UI", 8.5, "bold"),
            relief="flat",
            pady=7,
            command=lambda: (self.audio.play("error"), status_line.config(text="❌ No ads available in your region — wiping folders anyway~")),
        ).pack(side="left", fill="x", expand=True, padx=(4, 0))

        self.root.update_idletasks()
        self.start_ghost_cursor(format_btn)

        remaining = [120]
        ticks = [0]

        def tick_ransom():
            if not self.ransom_active or self.wipe_started or not self.fs.winfo_exists():
                return
            ticks[0] += 1
            if ticks[0] <= 2:
                remaining[0] -= 1
                self.audio.play("tick")
            else:
                taunt_lbl.config(text="Zafkiel: Aleph! Too slow~", fg="#ff3366")
                remaining[0] = max(0, remaining[0] - 24)
                self.audio.play("tock")

            mins, secs = divmod(remaining[0], 60)
            timer_lbl.config(text=f"{mins:02d}:{secs:02d}")

            if remaining[0] <= 0:
                self.start_fake_wipe("Time expired! Executing full system wipe...")
            else:
                self.root.after(750, tick_ransom)

        self.root.after(750, tick_ransom)

    # =========================================================
    # STAGE 7: FAKE FULL C:\ DRIVE WIPE CASCADE
    # =========================================================
    def start_fake_wipe(self, reason: str):
        if self.wipe_started:
            return
        self.wipe_started = True
        self.ransom_active = False
        self.stop_ghost_cursor()
        self.audio.play("alarm")

        for widget in self.fs.winfo_children():
            widget.destroy()

        self.fs.configure(bg="#050001", cursor="none")
        left_x = -self.vx + 40
        top_y = -self.vy + 35

        tk.Label(
            self.fs,
            text=f"⚠️ {reason}",
            fg="#ff2a55",
            bg="#050001",
            font=("Consolas", 15, "bold"),
        ).place(x=left_x, y=top_y)

        console_box = tk.Frame(self.fs, bg="#050001")
        console_box.place(x=left_x, y=top_y + 50, width=self.fs.winfo_screenwidth() - 80, height=500)

        commands = [
            f"C:\\Windows\\system32> del /f /s /q C:\\Users\\{self.victim_user}\\Desktop\\*.*",
            f"[DELETED] C:\\Users\\{self.victim_user}\\Documents\\passwords_backup.txt",
            f"[DELETED] C:\\Users\\{self.victim_user}\\Pictures\\Screenshots\\*.*",
            f"[DELETED] C:\\Users\\{self.victim_user}\\AppData\\Local\\Google\\Chrome\\User Data\\*.*",
            "[DELETED] C:\\Program Files (x86)\\Steam\\steamapps\\*.*",
            "[DELETED] C:\\Windows\\System32\\drivers\\etc\\hosts",
            "[DELETED] C:\\Windows\\System32\\ntoskrnl.exe",
            "[WIPED] C:\\ Drive — 0 bytes remaining. Formatting Master Boot Record...",
        ]

        def print_line(idx=0):
            if idx < len(commands):
                is_last = idx == len(commands) - 1
                tk.Label(
                    console_box,
                    text=commands[idx],
                    fg="white" if is_last else "#ff6680",
                    bg="#050001",
                    font=("Consolas", 12, "bold" if is_last else "normal"),
                    anchor="w",
                ).pack(fill="x", pady=3)
                self.audio.play("tick" if idx % 2 == 0 else "tock")
                self.root.after(300, lambda: print_line(idx + 1))
            else:
                self.root.after(950, self.show_thank_you_screen)

        print_line(0)

    # =========================================================
    # STAGE 8: CINEMATIC FADE-IN REVEAL
    # =========================================================
    def show_thank_you_screen(self):
        self.stop_ghost_cursor()
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
            text="Thanks for trying out Project Nightmare!\nNo files were encrypted, deleted, or broadcast.",
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
            command=self.cleanup_and_exit,
        ).pack(pady=8)

        def fade(alpha):
            if alpha <= 1.0:
                self.fs.attributes("-alpha", alpha)
                self.root.after(35, lambda: fade(alpha + 0.05))

        fade(0.0)


if __name__ == "__main__":
    KurumiFinalNightmare()