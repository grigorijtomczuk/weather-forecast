import tkinter as tk
from tkinter import filedialog, ttk


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
        if path:
            print("Файл выбран:", path)


if __name__ == "__main__":
    App().mainloop()
