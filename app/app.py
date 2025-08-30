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


if __name__ == "__main__":
    App().mainloop()
