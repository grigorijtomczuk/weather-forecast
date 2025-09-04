import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Глобальные параметры графиков
plt.rcParams["figure.figsize"] = (5, 2)
plt.rcParams["font.size"] = 5
plt.rcParams["lines.markersize"] = 1
plt.rcParams["lines.linewidth"] = 1


def moving_average_forecast(series, n=5, horizon=5):
    """Функция для прогноза на основе скользящего среднего."""
    values = list(series.astype(float))
    forecast = []
    for _ in range(horizon):
        window = (
            values[-n:] if len(values) >= n else values
        )  # Берём последние n значений
        average = float(np.mean(window))  # Считаем среднее по окну
        forecast.append(average)
        values.append(average)  # Добавляем прогноз в конец для следующего окна
    return np.array(forecast)

class App(tk.Tk):
    """Класс приложения tkinter."""

    def __init__(self):
        super().__init__()
        self.title("Прогноз погоды")
        self.geometry("1600x1200")
        self.data = pd.DataFrame()
        self.records = []  # Список объектов WeatherRecord

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
        ttk.Button(top, text="Построить графики", command=self.draw_plots).pack(
            side="left", padx=10
        )
        ttk.Button(top, text="Сохранить графики", command=self.save_plots).pack(
            side="left"
        )

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
            # Создаём список WeatherRecord для дальнейшей работы
            self.records = [
                WeatherRecord.from_series(row) for _, row in self.data.iterrows()
            ]
            self.refresh_table()
            self.draw_plots()
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
        """Построение графиков."""
        if self.data.empty:
            return
        n = max(1, int(self.n_var.get()))
        h = max(1, int(self.h_var.get()))

        dates = self.data["date"]
        self.ax1.clear()
        # График минимальной температуры
        self.ax1.plot(
            dates, self.data["t_min"], marker="o", label="T min (°C)", color="blue"
        )
        # График максимальной температуры
        self.ax1.plot(
            dates,
            self.data["t_max"],
            marker="o",
            label="T max (°C)",
            color="red",
        )
        # График средней температуры
        self.ax1.plot(dates, self.data["t_avg"], marker="o", label="T avg (°C)")
        self.ax1.set_title("Температура по дням")
        self.ax1.set_xlabel("Дата")
        self.ax1.set_ylabel("Температура, °C")
        self.ax1.tick_params(axis="both")
        self.ax1.grid(True, alpha=0.3)
        self.ax1.legend()
        self.canvas1.draw()

        self.ax2.clear()
        # Скользящее среднее по средней температуре
        moving_average = self.data["t_avg"].rolling(window=n, min_periods=1).mean()
        # Прогноз на h дней вперёд
        forecast = moving_average_forecast(self.data["t_avg"], n=n, horizon=h)
        last_date = self.data["date"].iloc[-1]
        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, h + 1)]
        self.ax2.plot(dates, self.data["t_avg"], marker="o", label="T avg (факт)")
        self.ax2.plot(dates, moving_average, label=f"Скользящая средняя (n={n})")
        self.ax2.plot(future_dates, forecast, marker="o", label=f"Прогноз на {h} дн.")
        self.ax2.set_title("Экстраполяция по скользящей средней")
        self.ax2.set_xlabel("Дата")
        self.ax2.set_ylabel("Температура, °C")
        self.ax2.tick_params(axis="both")
        self.ax2.grid(True, alpha=0.3)
        self.ax2.legend()
        self.canvas2.draw()

        # Нахождение и отображение макс и мин перепадов температур
        if self.records:
            max_record = max(self.records, key=lambda r: r.swing)
            min_record = min(self.records, key=lambda r: r.swing)
            self.title(
                f"Сильнейший перепад: {max_record.swing:.1f} °C ({max_record.date.date()}); "
                f"Слабейший: {min_record.swing:.1f} °C ({min_record.date.date()})"
            )

    def save_plots(self):
        """Сохранение графиков в выбранную папку."""
        if self.data.empty:
            return
        outdir = filedialog.askdirectory(title="Папка для сохранения графиков")
        if not outdir:
            return
        self.fig1.savefig(os.path.join(outdir, "Температура по дням.png"), dpi=150)
        self.fig2.savefig(
            os.path.join(outdir, "Экстраполяция по скользящей средней.png"), dpi=150
        )
        messagebox.showinfo("Готово", "Графики сохранены")



class WeatherRecord:
    def __init__(self, date, city, t_min, t_max, t_avg, description):
        self.date = pd.to_datetime(date)
        self.city = city
        self.t_min = float(t_min)
        self.t_max = float(t_max)
        self.t_avg = float(t_avg)
        self.description = description
        self.swing = self.t_max - self.t_min

    @classmethod
    def from_series(cls, row):
        return cls(
            row["date"],
            row.get("city", ""),
            row["t_min"],
            row["t_max"],
            row["t_avg"],
            row.get("description", ""),
        )

    def as_tuple(self):
        return (
            self.date.date(),
            self.city,
            round(self.t_min, 1),
            round(self.t_max, 1),
            round(self.t_avg, 1),
            self.description,
            round(self.swing, 1),
        )


if __name__ == "__main__":
    App().mainloop()
