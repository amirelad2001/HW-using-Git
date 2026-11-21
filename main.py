import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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
        self.student_ids = []
        self.original_grades = []
        self.corrected_grades = []
        self.selected_file = ""

        self.setWindowTitle("Grade Correction")
        self.resize(960, 720)
        self.setMinimumSize(760, 560)

        title = QLabel("Grade Correction")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Load a grades file and review the corrected scores.")
        subtitle.setObjectName("pageSubtitle")

        self.load_button = QPushButton("Load Grades File")
        self.load_button.setObjectName("primaryButton")
        self.load_button.clicked.connect(self.choose_file)

        self.update_button = QPushButton("Update File")
        self.update_button.setObjectName("secondaryButton")
        self.update_button.clicked.connect(self.update_file)

        self.about_button = QPushButton("About")
        self.about_button.setObjectName("textButton")
        self.about_button.clicked.connect(self.show_about)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addWidget(self.load_button)
        actions.addWidget(self.update_button)
        actions.addStretch()
        actions.addWidget(self.about_button)

        self.bonus_input = QLineEdit()
        self.bonus_input.setObjectName("bonusInput")
        self.bonus_input.setPlaceholderText("Enter bonus points")
        self.bonus_input.setValidator(QIntValidator(0, 100, self.bonus_input))
        self.bonus_input.returnPressed.connect(self.apply_bonus)

        bonus_label = QLabel("Bonus points")
        bonus_label.setObjectName("fieldLabel")
        bonus_hint = QLabel("Press Enter to apply the bonus.")
        bonus_hint.setObjectName("fieldHint")

        bonus_layout = QGridLayout()
        bonus_layout.setHorizontalSpacing(16)
        bonus_layout.setVerticalSpacing(5)
        bonus_layout.addWidget(bonus_label, 0, 0)
        bonus_layout.addWidget(self.bonus_input, 1, 0)
        bonus_layout.addWidget(bonus_hint, 1, 1)
        bonus_layout.setColumnStretch(0, 1)
        bonus_layout.setColumnStretch(1, 2)

        self.grades_table = QTableWidget(50, 3)
        self.grades_table.setObjectName("gradesTable")
        self.grades_table.setHorizontalHeaderLabels(
            ["ID", "Original Grades", "Corrected Grades"]
        )
        self.grades_table.horizontalHeader().setStretchLastSection(True)
        self.grades_table.horizontalHeader().setMinimumSectionSize(120)
        self.grades_table.verticalHeader().setVisible(False)
        self.grades_table.setAlternatingRowColors(True)
        self.grades_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.grades_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        content = QWidget()
        content.setObjectName("content")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 26, 30, 30)
        layout.setSpacing(18)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(actions)
        layout.addWidget(self.make_card(bonus_layout, "bonusCard"))
        layout.addWidget(self.grades_table, 1)
        self.setCentralWidget(content)

    @staticmethod
    def make_card(inner_layout: QGridLayout, object_name: str) -> QWidget:
        card = QWidget()
        card.setObjectName(object_name)
        card.setLayout(inner_layout)
        return card

    def choose_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Grades File",
            "",
            "CSV files (*.csv)",
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str) -> None:
        self.selected_file = file_path
        self.student_ids = []
        self.original_grades = []
        self.corrected_grades = []

        with open(file_path, 'r') as f:
            self.header = f.readline()
            for line in f:
                line = line.strip()
                parts = line.split(',')
                self.student_ids.append(parts[0])
                self.original_grades.append(int(parts[1]))
                self.corrected_grades.append(int(parts[1]))

        self.update_table()

    def update_table(self) -> None:
        columns = (
            self.student_ids,
            self.original_grades,
            self.corrected_grades,
        )
        for row in range(self.grades_table.rowCount()):
            for column, values in enumerate(columns):
                value = values[row] if row < len(values) else ""
                item = QTableWidgetItem(str(value)) if value != "" else None
                if item is not None:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignVCenter
                        | Qt.AlignmentFlag.AlignLeft
                    )
                self.grades_table.setItem(row, column, item)

    def apply_bonus(self) -> None:
        if self.bonus_input.text() != "":
            bonus = int(self.bonus_input.text())
            for i in range(len(self.original_grades)):
                grade = self.original_grades[i] + bonus
                if grade > 100:
                    grade = 100
                self.corrected_grades[i] = grade
            self.update_table()

    def update_file(self) -> None:
        if self.selected_file != "":
            with open(self.selected_file, 'w') as f:
                f.write(self.header)
                for i in range(len(self.student_ids)):
                    f.write(self.student_ids[i] + "," + str(self.corrected_grades[i]) + "\n")

        if not self.selected_file:
            QMessageBox.information(
                self,
                "No file selected",
                "Load a grades file before opening it.",
            )
            return

        try:
            if not os.path.isfile(self.selected_file):
                raise FileNotFoundError(self.selected_file)
            if sys.platform.startswith("win"):
                os.startfile(self.selected_file)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.selected_file])
            else:
                subprocess.Popen(["xdg-open", self.selected_file])
        except OSError as error:
            QMessageBox.warning(
                self,
                "Unable to open file",
                f"The file could not be opened in the default application:\n{error}",
            )

    def show_about(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.setObjectName("aboutDialog")
        dialog.setMinimumWidth(390)

        heading = QLabel("About this project")
        heading.setObjectName("dialogTitle")
        details = QLabel(
            "<b>Name:</b> Amir Elad<br>"
            "<b>Course:</b> practical programming <br>"
            "<b>Assignment:</b> Grade Correction Application"
        )
        details.setObjectName("aboutDetails")
        details.setTextFormat(Qt.TextFormat.RichText)
        repository = QLabel(
            '<a href="https://github.com/amirelad2001/HW-using-Git">'
            "Visit the public GitHub repository</a>"
        )
        repository.setObjectName("repositoryLink")
        repository.setOpenExternalLinks(True)
        repository.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )

        close_button = QPushButton("Close")
        close_button.setObjectName("primaryButton")
        close_button.clicked.connect(dialog.accept)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(16)
        layout.addWidget(heading)
        layout.addWidget(details)
        layout.addWidget(repository)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
        dialog.exec()


def main() -> int:
    app = QApplication(sys.argv)
    stylesheet_path = Path(__file__).with_name("style.qss")
    app.setStyleSheet(stylesheet_path.read_text(encoding="utf-8"))
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
