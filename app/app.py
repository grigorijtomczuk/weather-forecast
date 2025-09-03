import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class App(tk.Tk):
    """Класс приложения tkinter."""

    def __init__(self):
        super().__init__()
        self.title("Прогноз погоды")
        self.geometry("1600x1200")
        self.data = pd.DataFrame()
        self.records = []  # Список записей

        # Зона настроек (верхняя панель)
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)
        ttk.Button(top, text="Открыть файл", command=self.open_file).pack(side="left")
        ttk.Label(top, text="n (скользящая):").pack(side="left", padx=(10, 4))
        self.n_var = tk.IntVar(
            value=5
        )  # Число значений для подсчета скользящей средней
        ttk.Entry(top, textvariable=self.n_var, width=5).pack(side="left")
        ttk.Label(top, text="Прогноз, дней:").pack(side="left", padx=(10, 4))
        self.h_var = tk.IntVar(value=7)  # Кол-во дней для прогнозирования
        ttk.Entry(top, textvariable=self.h_var, width=5).pack(side="left")
        ttk.Button(top, text="Построить графики").pack(side="left", padx=10)
        ttk.Button(top, text="Сохранить графики").pack(side="left")

        # Зона таблицы (отображение данных)
        self.tree = ttk.Treeview(
            self,
            columns=("date", "city", "t_min", "t_max", "t_avg", "description", "swing"),
            show="headings",
        )
        for column, width, display_name in [
            ("date", 120, "Дата"),
            ("city", 150, "Город"),
            ("t_min", 80, "Т. min, °C"),
            ("t_max", 80, "Т. max, °C"),
            ("t_avg", 80, "Т. avg, °C"),
            ("description", 220, "Описание"),
            ("swing", 80, "Перепад, °C"),
        ]:
            self.tree.heading(column, text=display_name)
            self.tree.column(column, width=width, anchor="center")
        vertical_scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscroll=vertical_scrollbar.set)
        self.tree.pack(
            side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10)
        )
        vertical_scrollbar.pack(side="left", fill="y")

        # Зона с графиками (справа)
        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))
        self.fig1, self.ax1 = plt.subplots()
        self.ax1.tick_params(axis="x", labelrotation=45)
        self.fig1.subplots_adjust(bottom=0.25)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=right)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True)

        self.fig2, self.ax2 = plt.subplots()
        self.ax2.tick_params(axis="x", labelrotation=45)
        self.fig2.subplots_adjust(bottom=0.25)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=right)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, pady=(8, 0))

    def open_file(self):
        """Открытие файла и загрузка данных."""
        path = filedialog.askopenfilename(
            title="Выберите CSV или JSON",
            filetypes=[("CSV", "*.csv"), ("JSON", "*.json"), ("All", "*.*")],
        )
        if not path:
            return
        try:
            if path.lower().endswith(".csv"):
                data = pd.read_csv(path)
            else:
                data = pd.read_json(path)
            if "date" not in data.columns:
                raise ValueError("В файле нет колонки 'date'")
            for column in ["t_min", "t_max", "t_avg"]:
                if column not in data.columns:
                    raise ValueError("Отсутствует колонка: " + column)
            data["date"] = pd.to_datetime(data["date"])
            data["swing"] = (
                data["t_max"] - data["t_min"]
            )  # Вычисляем перепад температур
            self.data = data.sort_values("date").reset_index(drop=True)
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh_table(self):
        """Обновление таблицы с данными."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        for record in self.records:
            self.tree.insert(
                "",
                "end",
                values=record.as_tuple(),
            )

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
