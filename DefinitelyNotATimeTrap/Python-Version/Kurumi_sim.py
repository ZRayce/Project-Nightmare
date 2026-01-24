import tkinter as tk
from tkinter import ttk
import random
import winsound
import time
import os
from PIL import Image, ImageTk, ImageSequence

class KurumiFinalNightmare:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.hover_count = 0
        
        # --- DYNAMIC PATH LOGIC ---
        # Detects the folder where the script is currently running
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Points specifically to your GIF folder and file
        self.gif_path = os.path.join(base_dir, "GIF", "tokisaki-kurumi.gif")
        
        # GLOBAL EMERGENCY EXIT: Press ESC at any time to kill the program
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        self.spawn_main_window()
        self.root.mainloop()

    def spawn_main_window(self):
        self.win = tk.Toplevel()
        self.win.title("Definitely No Suspicious Spirit")
        self.win.geometry("450x280")
        
        # Center the window on your screen
        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        self.win.geometry(f"+{(sw-450)//2}+{(sh-280)//2}")
        
        self.win.configure(bg="#0d0d0d")
        self.win.attributes("-topmost", True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None) # Disable 'X' button

        tk.Label(self.win, text="D-Dokutah.. *sniff*\nZafkiel is hungry for your time...", 
                 fg="#ff4d4d", bg="#0d0d0d", font=("Courier", 11)).pack(pady=20)

        self.btn_stop = tk.Button(self.win, text="   Th-thanks   ", bg="#330000", fg="white", font=("Arial", 10, "bold"))
        self.btn_stop.pack(pady=10)
        self.btn_stop.bind("<Enter>", self.handle_hover)

    def handle_hover(self, event):
        self.hover_count += 1
        if self.hover_count < 4:
            winsound.Beep(600, 100)
            # Button jumps to a random spot
            self.btn_stop.place(x=random.randint(50, 350), y=random.randint(80, 220))
        else:
            self.trigger_phase_2()

    def trigger_phase_2(self):
        self.win.destroy()
        self.fs = tk.Toplevel()
        self.fs.attributes("-fullscreen", True, "-topmost", True)
        self.fs.configure(bg="black")
        self.fs.config(cursor="none") # Hide mouse cursor for realism

        self.center_frame = tk.Frame(self.fs, bg="black")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Load and play the Kurumi GIF
        try:
            img = Image.open(self.gif_path)
            self.frames = [ImageTk.PhotoImage(f.copy().convert("RGBA")) for f in ImageSequence.Iterator(img)]
            self.gif_label = tk.Label(self.center_frame, bg="black")
            self.gif_label.pack(pady=20)
            self.animate_gif(self.gif_label, 0)
        except Exception as e:
            tk.Label(self.center_frame, text=f"GIF NOT FOUND\nCheck: {self.gif_path}", fg="red", bg="black").pack()

        # Progress Bar Styling
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Red.Horizontal.TProgressbar", background='#990000', thickness=20)
        
        self.progress = ttk.Progressbar(self.center_frame, length=500, mode="determinate", style="Red.Horizontal.TProgressbar")
        self.progress.pack(pady=20)
        
        self.log_label = tk.Label(self.center_frame, text="ZAFKIEL PROTOCOL: 0%", fg="#ff0000", bg="black", font=("Courier", 14))
        self.log_label.pack()

        self.run_fake_deletion()

    def animate_gif(self, label, counter):
        # Loops the frames of the GIF
        frame = self.frames[counter]
        label.configure(image=frame)
        self.root.after(100, lambda: self.animate_gif(label, (counter + 1) % len(self.frames)))

    def run_fake_deletion(self):
        def step(p):
            if p <= 100:
                self.progress['value'] = p
                self.log_label.config(text=f"CORRUPTING REALITY: {p}%")
                if p % 10 == 0: winsound.Beep(800 + (p*5), 50)
                self.root.after(40, lambda: step(p + 1))
            else:
                self.trigger_bsod()
        step(0)

    def trigger_bsod(self):
        # Glitch Flicker effect
        for _ in range(10):
            self.fs.configure(bg=random.choice(["#0078d7", "black", "red"]))
            self.fs.update()
            time.sleep(0.05)
        
        self.center_frame.destroy()
        self.fs.configure(bg="#0078d7") # Windows Blue
        
        self.bsod_lbl = tk.Label(self.fs, text="", fg="white", bg="#0078d7", 
                                 font=("Segoe UI", 22), justify="left", wraplength=1000)
        self.bsod_lbl.place(relx=0.1, rely=0.3)

        def update_bsod(p):
            if p <= 100:
                bsod_text = (":(\n\nYour PC ran into a problem and needs to restart.\n\n"
                             f"{p}% complete\n\n"
                             "Stop code: SPIRIT_TIME_LEAK_KURUMI")
                self.bsod_lbl.config(text=bsod_text)
                self.root.after(80, lambda: update_bsod(p + 1))
            else:
                self.show_thank_you_screen()
        update_bsod(0)

    def show_thank_you_screen(self):
        # Clear BSOD widgets
        for widget in self.fs.winfo_children():
            widget.destroy()
            
        self.fs.configure(bg="black", cursor="arrow") # Restore mouse
        self.fs.attributes("-alpha", 0.0) # Start fully transparent
        
        thanks_frame = tk.Frame(self.fs, bg="black")
        thanks_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Display Kurumi one last time
        try:
            final_gif_label = tk.Label(thanks_frame, bg="black")
            final_gif_label.pack(pady=10)
            self.animate_gif(final_gif_label, 0)
        except:
            pass

        tk.Label(thanks_frame, text="ARA ARA~!", fg="#ff4d4d", bg="black", font=("Courier", 40, "bold")).pack()
        tk.Label(thanks_frame, text="Thanks for trying out the Kurumi 'Virus'!\nNo files were actually harmed.", 
                 fg="white", bg="black", font=("Arial", 16)).pack(pady=20)
        tk.Label(thanks_frame, text="[ Press ESC to Exit ]", fg="#444444", bg="black", font=("Arial", 10)).pack()

        # Cinematic Fade-in
        def fade(alpha):
            if alpha <= 1.0:
                self.fs.attributes("-alpha", alpha)
                self.root.after(40, lambda: fade(alpha + 0.05))
        
        fade(0.0)

if __name__ == "__main__":
    KurumiFinalNightmare()