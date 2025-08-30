import tkinter as tk
from tkinter import filedialog, ttk

import pandas as pd


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Прогноз погоды")
        self.geometry("1600x1200")

        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)
        ttk.Button(top, text="Открыть файл", command=self.open_file).pack(side="left")

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Выберите CSV или JSON",
            filetypes=[("CSV", "*.csv"), ("JSON", "*.json")],
        )
        if not path:
            return
        try:
            if path.lower().endswith(".csv"):
                self.data = pd.read_csv(path)
            else:
                self.data = pd.read_json(path)
            print(self.data.head())
        except Exception as e:
            print("Ошибка:", e)


if __name__ == "__main__":
    App().mainloop()
