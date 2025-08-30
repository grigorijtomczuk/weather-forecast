import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Прогноз погоды")
        self.geometry("1600x1200")

        # Правая панель для графиков
        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))

        self.fig1, self.ax1 = plt.subplots()
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=right)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True)

        self.fig2, self.ax2 = plt.subplots()
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=right)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, pady=(8, 0))

    def draw_plots(self):
        if self.data.empty:
            return

        dates = self.data["date"]

        self.ax1.clear()
        self.ax1.plot(
            dates, self.data["t_min"], marker="o", label="T min (°C)", color="blue"
        )
        self.ax1.plot(
            dates, self.data["t_max"], marker="o", label="T max (°C)", color="red"
        )
        self.ax1.plot(dates, self.data["t_avg"], marker="o", label="T avg (°C)")

        self.ax1.set_title("Температура по дням")
        self.ax1.set_xlabel("Дата")
        self.ax1.set_ylabel("Температура, °C")
        self.ax1.legend()
        self.ax1.grid(True, alpha=0.3)

        self.canvas1.draw()

        self.ax2.clear()
        n = 5
        moving_average = self.data["t_avg"].rolling(window=n, min_periods=1).mean()
        self.ax2.plot(dates, self.data["t_avg"], marker="o", label="T avg (факт)")
        self.ax2.plot(dates, moving_average, label=f"Скользящая средняя (n={n})")

        self.ax2.set_title("Скользящая средняя по T avg")
        self.ax2.legend()
        self.ax2.grid(True, alpha=0.3)
        self.canvas2.draw()


if __name__ == "__main__":
    App().mainloop()
