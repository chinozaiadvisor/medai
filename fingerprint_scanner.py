"""

ZKTeco Live20R orqali barmoq izini jonli ko'rish va MedAI uchun
128x128 px o'lchamda saqlash dasturi.

Talablar:
    pip install pyzkfp pillow
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import time
import os
from datetime import datetime

from pyzkfp import ZKFP2


class FingerprintScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MedAI — Barmoq Izi Skaneri")
        self.root.geometry("480x720")
        self.root.configure(bg="#0d1226")
        self.root.resizable(False, False)

        self.save_folder = os.path.join(os.path.dirname(__file__), "static", "uploads")
        os.makedirs(self.save_folder, exist_ok=True)

        self.zkfp2 = None
        self.device_opened = False
        self.live_running = False
        self.current_image = None  # PIL Image — eng so'nggi olingan kadr

        self._build_ui()
        self._init_device()


    def _build_ui(self):
        title = tk.Label(
            self.root, text="MedAI Barmoq Izi Skaneri",
            font=("Arial", 18, "bold"), fg="#00f0dc", bg="#0d1226"
        )
        title.pack(pady=(20, 5))

        subtitle = tk.Label(
            self.root, text="ZKTeco Live20R",
            font=("Arial", 10), fg="#64748b", bg="#0d1226"
        )
        subtitle.pack(pady=(0, 15))

        self.preview_frame = tk.Frame(self.root, bg="#000000", width=300, height=400)
        self.preview_frame.pack(pady=10)
        self.preview_frame.pack_propagate(False)

        self.preview_label = tk.Label(self.preview_frame, bg="#000000")
        self.preview_label.pack(expand=True)

   
        self.status_label = tk.Label(
            self.root, text="Qurilma qidirilmoqda...",
            font=("Arial", 10), fg="#64748b", bg="#0d1226"
        )
        self.status_label.pack(pady=(10, 5))

        folder_frame = tk.Frame(self.root, bg="#0d1226")
        folder_frame.pack(pady=10, fill="x", padx=30)

        self.folder_label = tk.Label(
            folder_frame, text=f"Papka: {self.save_folder}",
            font=("Arial", 8), fg="#94a3b8", bg="#0d1226",
            wraplength=460, justify="left"
        )
        self.folder_label.pack(side="left", fill="x", expand=True)

        folder_btn = tk.Button(
            folder_frame, text="Tanlash", font=("Arial", 9, "bold"),
            bg="#1e293b", fg="#00f0dc", relief="flat", padx=10,
            command=self.choose_folder
        )
        folder_btn.pack(side="right")


        btn_frame = tk.Frame(self.root, bg="#0d1226")
        btn_frame.pack(pady=20)

        self.capture_btn = tk.Button(
            btn_frame, text="📸  Rasmga Olish", font=("Arial", 13, "bold"),
            bg="#00c4b0", fg="#03050f", relief="flat",
            padx=30, pady=12, command=self.capture_fingerprint,
            state="disabled"
        )
        self.capture_btn.pack(side="left", padx=8)

        exit_btn = tk.Button(
            btn_frame, text="Chiqish", font=("Arial", 11),
            bg="#1e293b", fg="#e2e8f0", relief="flat",
            padx=20, pady=12, command=self.on_close
        )
        exit_btn.pack(side="left", padx=8)

        self.last_saved_label = tk.Label(
            self.root, text="", font=("Arial", 9, "bold"),
            fg="#00f0dc", bg="#0d1226"
        )
        self.last_saved_label.pack(pady=(5, 10))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _init_device(self):
        try:
            self.zkfp2 = ZKFP2()
            self.zkfp2.Init()
            count = self.zkfp2.GetDeviceCount()

            if count == 0:
                self.status_label.config(text="⚠ Qurilma topilmadi", fg="#ff4d6d")
                messagebox.showerror("Xato", "ZKTeco qurilma topilmadi. USB ulanishini tekshiring.")
                return

            self.zkfp2.OpenDevice(0)
            self.device_opened = True
            self.status_label.config(text="✅ Qurilma ulandi — barmog'ingizni qo'ying", fg="#00f0dc")
            self.capture_btn.config(state="normal")

  
            self.live_running = True
            threading.Thread(target=self._live_preview_loop, daemon=True).start()

        except Exception as e:
            self.status_label.config(text=f"⚠ Xato: {e}", fg="#ff4d6d")
            messagebox.showerror("Xato", f"Qurilmani ishga tushirishda xato:\n{e}")

    def _live_preview_loop(self):
        while self.live_running and self.device_opened:
            try:
                capture = self.zkfp2.AcquireFingerprint()
                if capture:
                    tmp, img = capture  

                    width = self.zkfp2.width
                    height = self.zkfp2.height

                    pil_img = Image.frombytes("L", (width, height), img)
                    self.current_image = pil_img

                    display_img = pil_img.resize((300, 400), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(display_img)

                    self.preview_label.config(image=tk_img)
                    self.preview_label.image = tk_img

            except Exception as e:
                print(f"DEBUG live loop xato: {e}")

            time.sleep(0.08)



  
    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.save_folder, title="Saqlash papkasini tanlang")
        if folder:
            self.save_folder = folder
            self.folder_label.config(text=f"Papka: {self.save_folder}")

 
    def capture_fingerprint(self):
        if self.current_image is None:
            messagebox.showwarning("Diqqat", "Hali barmoq izi olinmadi. Barmog'ingizni skaner ustiga qo'ying.")
            return

        try:
        
            img_128 = self.current_image.convert("RGB")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fingerprint_{timestamp}.png"
            filepath = os.path.join(self.save_folder, filename)

            img_128.save(filepath, "PNG")

            self.last_saved_label.config(text=f"✅ Saqlandi: {filename}")
            messagebox.showinfo("Muvaffaqiyatli", f"Rasm saqlandi:\n{filepath}\n\nO'lcham: {img_128.size[0]}x{img_128.size[1]} px (original)")

        except Exception as e:
            messagebox.showerror("Xato", f"Saqlashda xato:\n{e}")

   
    def on_close(self):
        self.live_running = False
        time.sleep(0.2)
        try:
            if self.device_opened:
                self.zkfp2.CloseDevice()
            if self.zkfp2:
                self.zkfp2.Terminate()
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FingerprintScannerApp(root)
    root.mainloop()