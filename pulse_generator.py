import tkinter as tk
from tkinter import messagebox
import numpy as np
import sounddevice as sd


class PulseGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор імпульсів 10-1000 Гц")
        self.root.geometry("360x220")
        self.root.resizable(False, False)

        self.sample_rate = 48000
        self.amplitude = 0.3
        self.stream = None
        self.phase = 0.0
        self.frequency = 100.0
        self.running = False

        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="Частота, Гц:", font=("Arial", 12)).pack(pady=(20, 5))

        self.freq_var = tk.StringVar(value="100")
        self.freq_entry = tk.Entry(self.root, textvariable=self.freq_var, font=("Arial", 12), justify="center")
        self.freq_entry.pack(pady=5)

        tk.Label(self.root, text="Діапазон: 10 ... 1000 Гц", font=("Arial", 10)).pack(pady=5)

        self.status_var = tk.StringVar(value="Статус: зупинено")
        tk.Label(self.root, textvariable=self.status_var, font=("Arial", 11)).pack(pady=10)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="Старт", width=12, command=self.start_signal, bg="lightgreen")
        self.start_btn.grid(row=0, column=0, padx=10)

        self.stop_btn = tk.Button(btn_frame, text="Стоп", width=12, command=self.stop_signal, bg="lightcoral", state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def audio_callback(self, outdata, frames, time_info, status):
        if status:
            print(status)

        t = (np.arange(frames) + self.phase) / self.sample_rate
        signal = self.amplitude * np.sign(np.sin(2 * np.pi * self.frequency * t))

        # щоб не було нулів у точках переходу
        signal[signal == 0] = self.amplitude

        outdata[:, 0] = signal.astype(np.float32)

        self.phase += frames
        # не даємо phase рости безкінечно
        if self.phase > self.sample_rate * 1000:
            self.phase = 0

    def start_signal(self):
        if self.running:
            return

        try:
            freq = float(self.freq_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Помилка", "Введи коректну частоту.")
            return

        if not (10 <= freq <= 1000):
            messagebox.showerror("Помилка", "Частота має бути в межах від 10 до 1000 Гц.")
            return

        self.frequency = freq
        self.phase = 0.0

        try:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                callback=self.audio_callback,
                blocksize=1024
            )
            self.stream.start()
        except Exception as e:
            messagebox.showerror("Помилка аудіо", f"Не вдалося запустити звуковий потік:\n{e}")
            self.stream = None
            return

        self.running = True
        self.status_var.set(f"Статус: працює, {self.frequency:.1f} Гц")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

    def stop_signal(self):
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        self.running = False
        self.status_var.set("Статус: зупинено")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def on_close(self):
        self.stop_signal()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PulseGeneratorApp(root)
    root.mainloop()