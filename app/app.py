import tkinter as tk
from tkinter import ttk

import pandas as pd


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Прогноз погоды")
        self.geometry("1600x1200")


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