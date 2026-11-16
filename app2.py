import csv
import sys
from pathlib import Path

from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT,
)
from matplotlib.figure import Figure
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Data Plotter")
        self.resize(1100, 650)

        self.filename: str | None = None
        self.month_list: list[str] = []
        self.rainfall_list: list[float] = []

        self.load_button = QPushButton("Load data")
        self.load_button.setObjectName("loadButton")
        self.load_button.clicked.connect(self.load_data)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.navigation_toolbar = NavigationToolbar2QT(self.canvas, self)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_title("Load a CSV file to view the chart")

        chart_layout = QVBoxLayout()
        chart_layout.setContentsMargins(18, 18, 18, 12)
        chart_layout.setSpacing(12)
        chart_layout.addWidget(self.load_button)
        chart_layout.addWidget(self.canvas)
        chart_layout.addWidget(self.navigation_toolbar)

        chart_panel = QWidget()
        chart_panel.setObjectName("chartPanel")
        chart_panel.setLayout(chart_layout)

        self.data_table = QTableWidget(0, 2)
        self.data_table.setObjectName("dataTable")
        self.data_table.setHorizontalHeaderLabels(["months", "rainfall [mm]"])
        self.data_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.data_table.setAlternatingRowColors(True)

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)
        layout.addWidget(chart_panel, 3)
        layout.addWidget(self.data_table, 2)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_data(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load data",
            "",
            "Data files (*.csv *.txt);;All files (*)",
        )
        if filename:
            self.filename = filename
            try:
                with open(filename, newline="", encoding="utf-8-sig") as file:
                    reader = csv.DictReader(file)
                    required_columns = {"Month", "Rainfall_mm"}
                    if reader.fieldnames is None or not required_columns.issubset(
                        reader.fieldnames
                    ):
                        raise ValueError(
                            "The CSV must contain Month and Rainfall_mm columns."
                        )

                    months: list[str] = []
                    rainfall: list[float] = []
                    for row_number, row in enumerate(reader, start=2):
                        month = row["Month"]
                        value = row["Rainfall_mm"]
                        if not month or value is None or not value.strip():
                            raise ValueError(
                                f"Missing month or rainfall value on row {row_number}."
                            )
                        try:
                            rainfall_value = float(value)
                        except ValueError as error:
                            raise ValueError(
                                f"Invalid rainfall value on row {row_number}: {value!r}."
                            ) from error
                        months.append(month)
                        rainfall.append(rainfall_value)

                if not months:
                    raise ValueError("The CSV does not contain any data rows.")
            except (OSError, UnicodeError, csv.Error, ValueError) as error:
                QMessageBox.warning(self, "Unable to load data", str(error))
                return

            self.month_list = months
            self.rainfall_list = rainfall
            self.update_table()
            self.draw_bar_chart()

    def update_table(self) -> None:
        self.data_table.setRowCount(len(self.month_list))
        for row, (month, rainfall) in enumerate(
            zip(self.month_list, self.rainfall_list)
        ):
            self.data_table.setItem(row, 0, QTableWidgetItem(month))
            self.data_table.setItem(row, 1, QTableWidgetItem(f"{rainfall:g}"))

    def draw_plot(self, x_values: list[str], y_values: list[float]) -> None:
        if len(x_values) != len(y_values):
            raise ValueError("x_values and y_values must have the same length")
        if not x_values:
            raise ValueError("The plot needs at least one data point")

        self.axes.clear()
        positions = list(range(len(x_values)))
        self.figure.set_facecolor("#f8fafc")
        self.axes.set_facecolor("#f8fafc")
        self.axes.fill_between(positions, y_values, color="#60a5fa", alpha=0.18)
        self.axes.plot(
            positions,
            y_values,
            color="#2563eb",
            linewidth=2.5,
            marker="o",
            markersize=6,
            markerfacecolor="#ffffff",
            markeredgecolor="#2563eb",
            markeredgewidth=1.8,
        )
        self.axes.set_xticks(positions, labels=x_values)
        self.axes.set_title(
            "Monthly Rainfall",
            color="#0f172a",
            fontsize=16,
            fontweight="bold",
            pad=16,
        )
        self.axes.set_xlabel("Month", color="#334155", labelpad=10)
        self.axes.set_ylabel("Rainfall (mm)", color="#334155", labelpad=10)
        self.axes.tick_params(colors="#475569")
        self.axes.grid(axis="y", color="#cbd5e1", linestyle="--", linewidth=0.8)
        self.axes.set_axisbelow(True)
        self.axes.spines["top"].set_visible(False)
        self.axes.spines["right"].set_visible(False)
        self.axes.spines["left"].set_color("#cbd5e1")
        self.axes.spines["bottom"].set_color("#cbd5e1")
        self.axes.margins(x=0.04, y=0.12)
        self.figure.tight_layout(pad=2)
        self.canvas.draw()

    def draw_bar_chart(self) -> None:
        if len(self.month_list) != len(self.rainfall_list):
            raise ValueError("month_list and rainfall_list must have the same length")
        if not self.month_list:
            raise ValueError("The bar chart needs at least one data point")

        self.axes.clear()
        self.figure.set_facecolor("#f8fafc")
        self.axes.set_facecolor("#f8fafc")
        highest_rainfall = max(self.rainfall_list)
        colors = [
            "#2563eb" if value == highest_rainfall else "#93c5fd"
            for value in self.rainfall_list
        ]
        bars = self.axes.bar(
            self.month_list,
            self.rainfall_list,
            color=colors,
            width=0.68,
            edgecolor="#ffffff",
            linewidth=0.8,
        )
        self.axes.bar_label(
            bars,
            labels=[f"{value:g}" for value in self.rainfall_list],
            padding=3,
            color="#475569",
            fontsize=9,
        )
        self.axes.set_title(
            "Monthly Rainfall",
            color="#0f172a",
            fontsize=16,
            fontweight="bold",
            pad=16,
        )
        self.axes.set_xlabel("Month", color="#334155", labelpad=10)
        self.axes.set_ylabel("Rainfall (mm)", color="#334155", labelpad=10)
        self.axes.tick_params(axis="x", labelrotation=45, colors="#475569")
        self.axes.tick_params(axis="y", colors="#475569")
        self.axes.grid(axis="y", color="#cbd5e1", linestyle="--", linewidth=0.8)
        self.axes.set_axisbelow(True)
        self.axes.spines["top"].set_visible(False)
        self.axes.spines["right"].set_visible(False)
        self.axes.spines["left"].set_color("#cbd5e1")
        self.axes.spines["bottom"].set_color("#cbd5e1")
        self.axes.margins(y=0.16)
        self.figure.tight_layout(pad=2)
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    stylesheet = Path(__file__).with_name("app2.qss")
    app.setStyleSheet(stylesheet.read_text(encoding="utf-8"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
