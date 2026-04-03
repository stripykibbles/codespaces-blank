import sys
import csv
import os
import re
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QDialog, QComboBox, QFileDialog,
    QSizePolicy, QFrame, QScrollArea, QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtGui import QFontDatabase, QCloseEvent


# ── Constants ────────────────────────────────────────────────────────────────

FIELDNAMES    = ["date", "time", "entry", "entry_word_count", "summary"]
ONWARD_DIR    = os.path.join(os.path.expanduser("~"), "Documents", "Onward")

FONT_OPTIONS = {
    "Sans Serif":  {"family": "Atkinson Hyperlegible",  "size": 14},
    "Serif":       {"family": "Crimson Text",            "size": 15},
    "Monospace":   {"family": "Courier Prime",           "size": 13},
}

PALETTE = {
    "bg":           "#ffffff",
    "sidebar_bg":   "#f8f8f8",
    "border":       "#e4e4e4",
    "btn_bg":       "#ebebeb",
    "btn_hover":    "#dbdbdb",
    "btn_pressed":  "#cccccc",
    "muted":        "#75767d",
    "text":         "#1a1a1a",
    "placeholder":  "#aaaaaa",
    "toast_bg":     "#e4e4e4",
}

SIDEBAR_WIDTH = 220
WINDOW_MIN_W  = 860
WINDOW_MIN_H  = 580


# ── Project path helpers ──────────────────────────────────────────────────────

def project_bundle(project_name: str) -> str:
    """Return the path to the .onward folder bundle for a given project name."""
    return os.path.join(ONWARD_DIR, f"{project_name}.onward")

def csv_path(project_name: str) -> str:
    return os.path.join(project_bundle(project_name), f"{project_name}.csv")

def txt_path(project_name: str) -> str:
    return os.path.join(project_bundle(project_name), f"{project_name}.txt")

def autosave_path(project_name: str) -> str:
    return os.path.join(project_bundle(project_name), "autosave.tmp")

def create_project(project_name: str) -> str | None:
    """Create a new .onward bundle. Returns error string or None on success."""
    bundle = project_bundle(project_name)
    if os.path.exists(bundle):
        return "A project with that name already exists."
    os.makedirs(bundle)
    return None


# ── Pure logic ────────────────────────────────────────────────────────────────

def get_characters(entry: str) -> int:
    chars = round(len(entry) / 3)
    return max(chars, 50)


def date_parse(t) -> tuple[str, str]:
    matched = re.match(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}).*$", str(t))
    if matched:
        return matched.group(1), matched.group(2)
    raise ValueError("Datetime not in expected format")


def date_format(d: str) -> str:
    date = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", d)
    if not date:
        raise ValueError("Date not in expected format")
    months = {
        "01": "January",  "02": "February", "03": "March",
        "04": "April",    "05": "May",       "06": "June",
        "07": "July",     "08": "August",    "09": "September",
        "10": "October",  "11": "November",  "12": "December",
    }
    month = months[date.group(2)]
    day   = date.group(3).lstrip("0")
    return f"{month} {day}, {date.group(1)}"


def get_word_count(project_name: str) -> int:
    count = 0
    try:
        with open(csv_path(project_name), "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                count += int(row["entry_word_count"])
    except FileNotFoundError:
        pass
    return count


def submit_entry(project_name: str, entry: str, summary: str):
    path = csv_path(project_name)
    date, time = date_parse(datetime.now())
    word_count  = len(entry.split())
    row = {"date": date, "time": time, "entry": entry,
           "entry_word_count": word_count, "summary": summary}
    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if new_file:
            writer.writeheader()
        writer.writerow(row)
    # Delete autosave on clean submit
    apath = autosave_path(project_name)
    if os.path.exists(apath):
        os.remove(apath)


def export_text(project_name: str) -> str:
    novel = ""
    with open(csv_path(project_name), "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            novel += row["entry"] + "\n\n"
    return novel


def load_summaries(project_name: str) -> list[tuple[str, str]]:
    rows = []
    with open(csv_path(project_name), "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append((row["date"], row["time"], row["summary"]))
    rows.sort(key=lambda r: (r[0], r[1]), reverse=True)
    return [(date_format(d), s) for d, t, s in rows]


def import_csv_file(project_name: str, path: str) -> str | None:
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or list(reader.fieldnames) != FIELDNAMES:
            return "CSV file is not in a valid format."
        rows = list(reader)
    dest = csv_path(project_name)
    new_file = not os.path.exists(dest)
    with open(dest, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if new_file:
            writer.writeheader()
        writer.writerows(rows)
    return None


def write_autosave(project_name: str, text: str):
    try:
        with open(autosave_path(project_name), "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        pass


def delete_autosave(project_name: str):
    try:
        apath = autosave_path(project_name)
        if os.path.exists(apath):
            os.remove(apath)
    except Exception:
        pass


def read_autosave(project_name: str) -> str | None:
    try:
        apath = autosave_path(project_name)
        if os.path.exists(apath):
            with open(apath, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    return None


# ── Stylesheet helpers ────────────────────────────────────────────────────────

def base_stylesheet(font_family: str, font_size: int) -> str:
    p = PALETTE
    return f"""
    QMainWindow, QWidget#central, QWidget#mainArea {{
        background-color: {p['bg']};
    }}
    QWidget#sidebar {{
        background-color: {p['sidebar_bg']};
        border-right: 1px solid {p['border']};
    }}
    QTextEdit#editor {{
        background-color: {p['bg']};
        color: {p['text']};
        border: none;
        font-family: "{font_family}";
        font-size: {font_size}pt;
        padding: 8px 4px;
        selection-background-color: {p['border']};
    }}
    QPushButton.sidebar-btn {{
        background-color: {p['btn_bg']};
        color: {p['text']};
        border: none;
        border-radius: 4px;
        padding: 7px 12px;
        font-family: "{font_family}";
        font-size: {font_size - 1}pt;
        text-align: center;
    }}
    QPushButton.sidebar-btn:hover  {{ background-color: {p['btn_hover']}; }}
    QPushButton.sidebar-btn:pressed {{ background-color: {p['btn_pressed']}; }}
    QLabel#wordCountLabel {{
        color: {p['text']};
        font-family: "{font_family}";
        font-size: {font_size - 1}pt;
        line-height: 1.4;
    }}
    QLabel#projectNameLabel {{
        color: {p['muted']};
        font-family: "{font_family}";
        font-size: {font_size - 2}pt;
    }}
    QLabel#muted {{
        color: {p['muted']};
        font-family: "{font_family}";
        font-size: {font_size - 2}pt;
    }}
    QDialog {{
        background-color: {p['bg']};
    }}
    QLabel.dialog-body {{
        color: {p['text']};
        font-family: "{font_family}";
        font-size: {font_size - 1}pt;
    }}
    QTextEdit.dialog-input {{
        background-color: {p['bg']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 4px;
        font-family: "{font_family}";
        font-size: {font_size - 1}pt;
        padding: 6px;
    }}
    QLineEdit.dialog-input {{
        background-color: {p['bg']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 4px;
        font-family: "{font_family}";
        font-size: {font_size - 1}pt;
        padding: 6px;
    }}
    QPushButton.dialog-btn {{
        background-color: {p['btn_bg']};
        color: {p['text']};
        border: none;
        border-radius: 4px;
        padding: 6px 16px;
        font-family: "{font_family}";
        font-size: {font_size - 1}pt;
    }}
    QPushButton.dialog-btn:hover   {{ background-color: {p['btn_hover']}; }}
    QPushButton.dialog-btn:pressed {{ background-color: {p['btn_pressed']}; }}
    QComboBox {{
        background-color: {p['btn_bg']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 4px;
        padding: 5px 10px;
        font-family: "{font_family}";
        font-size: {font_size - 1}pt;
    }}
    QComboBox::drop-down {{ border: none; }}
    QScrollArea, QScrollArea > QWidget > QWidget {{
        background-color: {p['bg']};
        border: none;
    }}
    QScrollBar:vertical {{
        background: {p['bg']};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {p['border']};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """

def launch_stylesheet(font_family: str, font_size: int) -> str:
    p = PALETTE
    return f"""
    QWidget#launchWidget {{
        background-color: {p['bg']};
    }}
    QLabel#launchTitle {{
        color: {p['text']};
        font-family: "{font_family}";
        font-size: {font_size + 6}pt;
        font-weight: bold;
    }}
    QPushButton.launch-btn {{
        background-color: {p['btn_bg']};
        color: {p['text']};
        border: none;
        border-radius: 4px;
        padding: 10px 24px;
        font-family: "{font_family}";
        font-size: {font_size}pt;
        min-width: 160px;
    }}
    QPushButton.launch-btn:hover   {{ background-color: {p['btn_hover']}; }}
    QPushButton.launch-btn:pressed {{ background-color: {p['btn_pressed']}; }}
    QLabel.dialog-body {{
        color: {p['text']};
        font-family: "{font_family}";
        font-size: {font_size - 1}pt;
    }}
    QLineEdit.dialog-input {{
        background-color: {p['bg']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 4px;
        font-family: "{font_family}";
        font-size: {font_size - 1}pt;
        padding: 6px;
    }}
    QPushButton.dialog-btn {{
        background-color: {p['btn_bg']};
        color: {p['text']};
        border: none;
        border-radius: 4px;
        padding: 6px 16px;
        font-family: "{font_family}";
        font-size: {font_size - 1}pt;
    }}
    QPushButton.dialog-btn:hover   {{ background-color: {p['btn_hover']}; }}
    QPushButton.dialog-btn:pressed {{ background-color: {p['btn_pressed']}; }}
    """


# ── Dialogs ───────────────────────────────────────────────────────────────────

class NewProjectDialog(QDialog):
    """Prompts user to enter a name for a new project."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_name = ""
        self.setWindowTitle("New Project")
        self.setFixedSize(360, 170)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        lbl = QLabel("Project name:")
        lbl.setProperty("class", "dialog-body")
        layout.addWidget(lbl)

        self.name_input = QLineEdit()
        self.name_input.setProperty("class", "dialog-input")
        self.name_input.setPlaceholderText("e.g. my-novel")
        self.name_input.returnPressed.connect(self._on_create)
        layout.addWidget(self.name_input)

        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet("color: #c0392b; font-size: 11pt;")
        self.error_lbl.setWordWrap(True)
        self.error_lbl.setVisible(False)
        layout.addWidget(self.error_lbl)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "dialog-btn")
        cancel_btn.clicked.connect(self.reject)
        create_btn = QPushButton("Create")
        create_btn.setProperty("class", "dialog-btn")
        create_btn.clicked.connect(self._on_create)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(create_btn)
        layout.addLayout(btn_row)

    def _on_create(self):
        name = self.name_input.text().strip()
        if not name:
            return
        error = create_project(name)
        if error:
            self.error_lbl.setText(error)
            self.error_lbl.setVisible(True)
            return
        self.project_name = name
        self.accept()


class SummaryDialog(QDialog):
    """Shows all entry summaries in reverse chronological order."""

    def __init__(self, project_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Summary")
        self.setMinimumSize(460, 380)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(4, 4, 8, 4)
        inner_layout.setSpacing(0)

        try:
            entries = load_summaries(project_name)
        except FileNotFoundError:
            entries = []

        if not entries:
            lbl = QLabel("A summary of your novel will go here!")
            lbl.setProperty("class", "dialog-body")
            lbl.setWordWrap(True)
            inner_layout.addWidget(lbl)
        else:
            for fmt_date, summary_text in entries:
                date_lbl = QLabel(fmt_date)
                date_lbl.setObjectName("muted")
                date_lbl.setStyleSheet(
                    f"background-color: {PALETTE['border']}; "
                    f"color: {PALETTE['muted']}; "
                    "padding: 2px 8px; "
                    "font-size: 10pt;"
                )
                inner_layout.addWidget(date_lbl)

                summary_frame = QFrame()
                summary_frame.setStyleSheet(
                    f"border-left: 2px solid {PALETTE['border']}; "
                    "margin-bottom: 12px;"
                )
                sf_layout = QVBoxLayout(summary_frame)
                sf_layout.setContentsMargins(10, 5, 0, 10)
                body = QLabel(summary_text if summary_text else "<i>No summary submitted.</i>")
                body.setProperty("class", "dialog-body")
                body.setWordWrap(True)
                body.setTextFormat(Qt.RichText)
                sf_layout.addWidget(body)
                inner_layout.addWidget(summary_frame)

        inner_layout.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll)

        close_btn = QPushButton("Close")
        close_btn.setProperty("class", "dialog-btn")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)


class AddSummaryDialog(QDialog):
    """Prompts user to enter a summary before submitting an entry."""

    def __init__(self, entry: str, parent=None):
        super().__init__(parent)
        self.entry   = entry
        self.summary = ""
        self.setWindowTitle("Add Summary")
        self.setMinimumSize(460, 260)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        hint = QLabel(
            "Jot down some notes for future reference. "
            "(Or not – that's okay, too!) "
            "The character limit is determined by the length of your entry."
        )
        hint.setProperty("class", "dialog-body")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.text_edit = PlainTextEditor()
        self.text_edit.setProperty("class", "dialog-input")
        self.text_edit.setFixedHeight(100)
        self.text_edit.textChanged.connect(self._enforce_limit)
        layout.addWidget(self.text_edit)

        self._char_limit = get_characters(entry)
        self.char_count_lbl = QLabel(f"0 / {self._char_limit} characters")
        self.char_count_lbl.setObjectName("muted")
        layout.addWidget(self.char_count_lbl)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "dialog-btn")
        cancel_btn.clicked.connect(self.reject)
        submit_btn = QPushButton("Submit")
        submit_btn.setProperty("class", "dialog-btn")
        submit_btn.clicked.connect(self._on_submit)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(submit_btn)
        layout.addLayout(btn_row)

    def _enforce_limit(self):
        text = self.text_edit.toPlainText()
        if len(text) > self._char_limit:
            cursor = self.text_edit.textCursor()
            pos    = cursor.position()
            self.text_edit.blockSignals(True)
            self.text_edit.setPlainText(text[: self._char_limit])
            cursor.setPosition(min(pos, self._char_limit))
            self.text_edit.setTextCursor(cursor)
            self.text_edit.blockSignals(False)
            text = self.text_edit.toPlainText()
        self.char_count_lbl.setText(f"{len(text)} / {self._char_limit} characters")

    def _on_submit(self):
        self.summary = self.text_edit.toPlainText()
        self.accept()


class SettingsDialog(QDialog):
    """Font picker."""

    def __init__(self, current_font: str, parent=None):
        super().__init__(parent)
        self.chosen_font = current_font
        self.setWindowTitle("Settings")
        self.setFixedSize(300, 140)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        lbl = QLabel("Select a font")
        lbl.setProperty("class", "dialog-body")
        layout.addWidget(lbl)

        self.combo = QComboBox()
        for name in FONT_OPTIONS:
            self.combo.addItem(name)
        self.combo.setCurrentText(current_font)
        layout.addWidget(self.combo)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("Save & Close")
        save_btn.setProperty("class", "dialog-btn")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _save(self):
        self.chosen_font = self.combo.currentText()
        self.accept()


class ExportDialog(QDialog):
    """Export TXT or CSV."""

    def __init__(self, project_name: str, parent=None):
        super().__init__(parent)
        self._project_name = project_name
        self.setWindowTitle("Export Work")
        self.setFixedSize(280, 130)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        txt_btn = QPushButton("Export Text (.txt)")
        txt_btn.setProperty("class", "dialog-btn")
        txt_btn.clicked.connect(self._export_txt)

        csv_btn = QPushButton("Export Raw Data (.csv)")
        csv_btn.setProperty("class", "dialog-btn")
        csv_btn.clicked.connect(self._export_csv)

        layout.addWidget(txt_btn)
        layout.addWidget(csv_btn)

        close_btn = QPushButton("Close")
        close_btn.setProperty("class", "dialog-btn")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)

    def _export_txt(self):
        default_name = f"{self._project_name}.txt"
        dest, _ = QFileDialog.getSaveFileName(self, "Save Text File", default_name, "Text Files (*.txt)")
        if dest:
            text = export_text(self._project_name)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(text)
            msg = QMessageBox(self)
            msg.setWindowTitle("Exported")
            msg.setText(f"Text saved to:\n{dest}")
            msg.setStyleSheet("QLabel { color: #1a1a1a; } QPushButton { color: #1a1a1a; background-color: #ebebeb; border: none; border-radius: 4px; padding: 6px 16px; }")
            msg.exec()

    def _export_csv(self):
        from datetime import datetime as dt
        timestamp = dt.now().strftime("%Y%m%d-%H%M%S")
        default_name = f"{self._project_name}-{timestamp}.csv"
        dest, _ = QFileDialog.getSaveFileName(self, "Save CSV File", default_name, "CSV Files (*.csv)")
        if dest:
            import shutil
            shutil.copy2(csv_path(self._project_name), dest)
            msg = QMessageBox(self)
            msg.setWindowTitle("Exported")
            msg.setText(f"CSV saved to:\n{dest}")
            msg.setStyleSheet("QLabel { color: #1a1a1a; } QPushButton { color: #1a1a1a; background-color: #ebebeb; border: none; border-radius: 4px; padding: 6px 16px; }")
            msg.exec()



# ── Plain text editor ─────────────────────────────────────────────────────────

class PlainTextEditor(QTextEdit):
    """QTextEdit that strips formatting on paste, keeping plain text only."""

    def insertFromMimeData(self, source):
        if source.hasText():
            self.insertPlainText(source.text())


# ── Toast notification ────────────────────────────────────────────────────────

class Toast(QLabel):
    """A small non-blocking notification that fades away."""

    def __init__(self, message: str, parent: QWidget):
        super().__init__(message, parent)
        self.setStyleSheet(
            f"background-color: {PALETTE['toast_bg']}; "
            f"color: {PALETTE['text']}; "
            "padding: 8px 16px; "
            "border-radius: 4px; "
            "font-size: 11pt;"
        )
        self.adjustSize()
        self._reposition(parent)
        self.show()
        QTimer.singleShot(2500, self.deleteLater)

    def _reposition(self, parent: QWidget):
        self.adjustSize()
        x = parent.width()  - self.width()  - 20
        y = parent.height() - self.height() - 20
        self.move(x, y)
        self.raise_()


# ── Launch screen ─────────────────────────────────────────────────────────────

class LaunchWindow(QMainWindow):
    """New Project / Open Project screen shown on every launch."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Onward")
        self.setFixedSize(400, 260)
        self._chosen_project = None

        central = QWidget()
        central.setObjectName("launchWidget")
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Onward")
        title.setObjectName("launchTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(8)

        new_btn = QPushButton("New Project")
        new_btn.setProperty("class", "launch-btn")
        new_btn.clicked.connect(self._on_new_project)
        layout.addWidget(new_btn, alignment=Qt.AlignCenter)

        open_btn = QPushButton("Open Project")
        open_btn.setProperty("class", "launch-btn")
        open_btn.clicked.connect(self._on_open_project)
        layout.addWidget(open_btn, alignment=Qt.AlignCenter)

        import_btn = QPushButton("Import")
        import_btn.setProperty("class", "launch-btn")
        import_btn.clicked.connect(self._on_import)
        layout.addWidget(import_btn, alignment=Qt.AlignCenter)

        fo = FONT_OPTIONS["Sans Serif"]
        self.setStyleSheet(launch_stylesheet(fo["family"], fo["size"]))

    def _on_new_project(self):
        dlg = NewProjectDialog(self)
        fo  = FONT_OPTIONS["Sans Serif"]
        dlg.setStyleSheet(base_stylesheet(fo["family"], fo["size"]))
        if dlg.exec() == QDialog.Accepted:
            self._chosen_project = dlg.project_name
            self._open_main_window()

    def _on_open_project(self):
        os.makedirs(ONWARD_DIR, exist_ok=True)

        import platform
        if platform.system() == "Darwin":
            # On Mac, .onward bundles are registered file types — use native picker
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Project",
                ONWARD_DIR,
                "Onward Projects (*.onward)"
            )
            bundle = path
        else:
            # On Windows, .onward bundles are folders — use directory picker
            bundle = QFileDialog.getExistingDirectory(
                self,
                "Open Project",
                ONWARD_DIR,
            )

        if bundle and bundle.endswith(".onward"):
            project_name = os.path.basename(bundle)[:-len(".onward")]
            self._chosen_project = project_name
            self._open_main_window()
        elif bundle:
            msg = QMessageBox(self)
            msg.setWindowTitle("Invalid Project")
            msg.setText("Please select a valid .onward project folder.")
            msg.setStyleSheet("QLabel { color: #1a1a1a; } QPushButton { color: #1a1a1a; background-color: #ebebeb; border: none; border-radius: 4px; padding: 6px 16px; }")
            msg.exec()

    def _on_import(self):
        # Step 1: select file
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import File",
            "",
            "Supported Files (*.csv *.txt);;CSV Files (*.csv);;Text Files (*.txt)"
        )
        if not path:
            return

        _, ext = os.path.splitext(path)
        ext = ext.lower()

        # Step 2: validate CSV early so we don't ask for a name on bad files
        if ext == ".csv":
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None or list(reader.fieldnames) != FIELDNAMES:
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Import Error")
                    msg.setText("CSV file is not in a valid Onward format.")
                    msg.setStyleSheet("QLabel { color: #1a1a1a; } QPushButton { color: #1a1a1a; background-color: #ebebeb; border: none; border-radius: 4px; padding: 6px 16px; }")
                    msg.exec()
                    return

        # Step 3: ask for project name
        dlg = NewProjectDialog(self)
        fo  = FONT_OPTIONS["Sans Serif"]
        dlg.setStyleSheet(base_stylesheet(fo["family"], fo["size"]))
        if dlg.exec() != QDialog.Accepted:
            return

        project_name = dlg.project_name

        # Step 4: import data into the new project
        if ext == ".csv":
            import_csv_file(project_name, path)
            self._chosen_project = project_name
            self._open_main_window(preload_text=None)
        elif ext == ".txt":
            with open(path, "r", encoding="utf-8") as f:
                txt_content = f.read()
            self._chosen_project = project_name
            self._open_main_window(preload_text=txt_content)

    def _open_main_window(self, preload_text: str | None = None):
        self._main = MainWindow(self._chosen_project, preload_text=preload_text)
        self._main.resize(1000, 680)
        self._main.show()
        self.hide()
        QApplication.instance().main_window = self._main


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):

    def __init__(self, project_name: str, preload_text: str | None = None):
        super().__init__()
        self._project_name = project_name
        self.setWindowTitle(f"Onward — {project_name}")
        self.setMinimumSize(WINDOW_MIN_W, WINDOW_MIN_H)
        self._current_font = "Sans Serif"
        self._unsaved = False

        # Autosave timer — writes every 3 minutes
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(3 * 60 * 1000)
        self._autosave_timer.timeout.connect(self._do_autosave)
        self._autosave_timer.start()

        self._build_ui()
        self._apply_font(self._current_font)
        self._refresh_sidebar()

        if preload_text:
            self._editor.setPlainText(preload_text)
            self._unsaved = True
        else:
            self._check_autosave_recovery()

    # ── Autosave ──────────────────────────────────────────────────────────────

    def _do_autosave(self):
        text = self._editor.toPlainText()
        if text.strip():
            write_autosave(self._project_name, text)

    def _check_autosave_recovery(self):
        recovered = read_autosave(self._project_name)
        if recovered:
            msg = QMessageBox(self)
            msg.setWindowTitle("Recover Unsaved Entry")
            msg.setText(
                "It looks like Onward closed unexpectedly. "
                "Would you like to recover your unsaved entry?"
            )
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            msg.setStyleSheet("QLabel { color: #1a1a1a; } QPushButton { color: #1a1a1a; background-color: #ebebeb; border: none; border-radius: 4px; padding: 6px 16px; }")
            if msg.exec() == QMessageBox.Yes:
                self._editor.setPlainText(recovered)
                self._unsaved = True
            else:
                delete_autosave(self._project_name)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        # Main writing area fills the full window
        main_area = QWidget()
        main_area.setObjectName("mainArea")
        main_area.setParent(central)
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(40, 30, 40, 30)

        self._editor = PlainTextEditor()
        self._editor.setObjectName("editor")
        self._editor.setPlaceholderText("It was a dark and stormy night...")
        self._editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._editor.textChanged.connect(self._on_text_changed)
        main_layout.addWidget(self._editor)

        # Toggle row — project name + >> in top-right, entire row is clickable
        self._toggle_row = QPushButton(f"{self._project_name}  >>")
        self._toggle_row.setParent(central)
        self._toggle_row.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_row.clicked.connect(self._toggle_sidebar)
        self._toggle_row.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; "
            f"color: {PALETTE['placeholder']}; font-size: 10pt; padding: 0; }}"
            f"QPushButton:hover {{ color: {PALETTE['text']}; }}"
        )
        self._toggle_row.adjustSize()

        # Sidebar overlays the writing area
        self._sidebar_widget = QWidget()
        self._sidebar_widget.setObjectName("sidebar")
        self._sidebar_widget.setParent(central)
        self._sidebar_widget.setFixedWidth(SIDEBAR_WIDTH)
        self._sidebar_widget.hide()

        sidebar_layout = QVBoxLayout(self._sidebar_widget)
        sidebar_layout.setContentsMargins(16, 48, 16, 20)
        sidebar_layout.setSpacing(8)
        self._word_count_lbl = QLabel()
        self._word_count_lbl.setObjectName("wordCountLabel")
        self._word_count_lbl.setWordWrap(True)
        sidebar_layout.addWidget(self._word_count_lbl)

        sidebar_layout.addSpacing(6)

        self._btn_submit   = self._sidebar_button("Submit && Clear")
        self._btn_view     = self._sidebar_button("View Summary")
        self._btn_export   = self._sidebar_button("Export Work")
        self._btn_settings = self._sidebar_button("Settings")
        self._btn_feedback = self._sidebar_button("Send Feedback")

        for btn in [self._btn_submit, self._btn_view, self._btn_export,
                    self._btn_settings]:
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self._btn_feedback)

        self._btn_submit.clicked.connect(self._on_submit)
        self._btn_view.clicked.connect(self._on_view_summary)
        self._btn_export.clicked.connect(self._on_export)
        self._btn_settings.clicked.connect(self._on_settings)
        self._btn_feedback.clicked.connect(self._on_feedback)

        # Root layout — just the main area, sidebar overlays on top
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(main_area)

        # Animation for sidebar slide
        self._sidebar_anim = QPropertyAnimation(self._sidebar_widget, b"geometry")
        self._sidebar_anim.setDuration(200)
        self._sidebar_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._sidebar_open = False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition_overlay_elements()

    def _reposition_overlay_elements(self):
        """Position sidebar and toggle row correctly."""
        h = self.centralWidget().height()
        w = self.centralWidget().width()

        if self._sidebar_open:
            # Expanded: left-aligned at sidebar left edge + 16px
            self._toggle_row.adjustSize()
            self._toggle_row.move(w - SIDEBAR_WIDTH + 16, 12)
        else:
            # Collapsed: right-aligned, 16px from right edge
            self._toggle_row.adjustSize()
            self._toggle_row.move(w - self._toggle_row.width() - 16, 12)

        self._toggle_row.raise_()

        # Sidebar covers full height on right side
        if self._sidebar_open:
            self._sidebar_widget.setGeometry(w - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, h)
        else:
            self._sidebar_widget.setGeometry(w, 0, SIDEBAR_WIDTH, h)
        self._sidebar_widget.raise_()

        # Toggle row is always the top layer
        self._toggle_row.raise_()

    def _toggle_sidebar(self):
        import warnings
        h = self.centralWidget().height()
        w = self.centralWidget().width()
        if self._sidebar_open:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    self._sidebar_anim.finished.disconnect()
                except Exception:
                    pass
            self._sidebar_anim.setStartValue(QRect(w - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, h))
            self._sidebar_anim.setEndValue(QRect(w, 0, SIDEBAR_WIDTH, h))
            self._sidebar_anim.finished.connect(lambda: self._sidebar_widget.hide())
            self._sidebar_anim.start()
            self._sidebar_open = False
            self._toggle_row.setText(f"{self._project_name}  >>")
            self._toggle_row.adjustSize()
            self._toggle_row.move(w - self._toggle_row.width() - 16, 12)
            self._toggle_row.raise_()
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    self._sidebar_anim.finished.disconnect()
                except Exception:
                    pass
            self._sidebar_widget.setGeometry(w, 0, SIDEBAR_WIDTH, h)
            self._sidebar_widget.show()
            self._sidebar_anim.setStartValue(QRect(w, 0, SIDEBAR_WIDTH, h))
            self._sidebar_anim.setEndValue(QRect(w - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, h))
            self._sidebar_anim.finished.connect(lambda: self._toggle_row.raise_())
            self._sidebar_anim.start()
            self._sidebar_open = True
            self._toggle_row.setText(f"<<  {self._project_name}")
            self._toggle_row.adjustSize()
            self._toggle_row.move(w - SIDEBAR_WIDTH + 16, 12)
            self._toggle_row.raise_()

    def mousePressEvent(self, event):
        """Close sidebar when clicking outside it."""
        if self._sidebar_open:
            sidebar_rect = self._sidebar_widget.geometry()
            if not sidebar_rect.contains(event.position().toPoint()):
                self._toggle_sidebar()
        super().mousePressEvent(event)

    def _sidebar_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setProperty("class", "sidebar-btn")
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setFixedHeight(34)
        return btn

    # ── Font / style ──────────────────────────────────────────────────────────

    def _apply_font(self, font_name: str):
        self._current_font = font_name
        fo = FONT_OPTIONS[font_name]
        self.setStyleSheet(base_stylesheet(fo["family"], fo["size"]))
        # Update toggle row and close button to match selected font
        self._toggle_row.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; "
            f"color: {PALETTE['placeholder']}; font-family: '{fo['family']}'; "
            f"font-size: 10pt; padding: 0; }}"
            f"QPushButton:hover {{ color: {PALETTE['text']}; }}"
        )
        self._toggle_row.adjustSize()
        # Reposition toggle row after font/size change
        self._reposition_overlay_elements()

    # ── Sidebar state ─────────────────────────────────────────────────────────

    def _refresh_sidebar(self):
        count = get_word_count(self._project_name)
        if count == 0:
            msg = "You've submitted 0 words.\n(It's going to be great.)"
        elif count == 1:
            msg = "You've submitted 1 word.\n(And it's a great start.)"
        else:
            msg = f"You've submitted {count} words.\n(And they're all amazing.)"
        self._word_count_lbl.setText(msg)

        has_csv = os.path.exists(csv_path(self._project_name))
        self._btn_view.setVisible(has_csv)
        self._btn_export.setVisible(has_csv)

    # ── Unsaved-changes guard ─────────────────────────────────────────────────

    def _on_text_changed(self):
        self._unsaved = bool(self._editor.toPlainText())

    def closeEvent(self, event: QCloseEvent):
        if self._unsaved:
            msg = QMessageBox(self)
            msg.setWindowTitle("Unsaved Entry")
            msg.setText("You have an unsaved entry. Are you sure you want to quit?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            msg.setStyleSheet("QLabel { color: #1a1a1a; } QPushButton { color: #1a1a1a; background-color: #ebebeb; border: none; border-radius: 4px; padding: 6px 16px; }")
            reply = msg.exec()
            if reply == QMessageBox.No:
                event.ignore()
                return
        delete_autosave(self._project_name)
        self._autosave_timer.stop()
        event.accept()

    # ── Button handlers ───────────────────────────────────────────────────────

    def _on_submit(self):
        entry = self._editor.toPlainText().strip()
        if not entry:
            self._show_toast("You have to write something first! :P")
            return

        dlg = AddSummaryDialog(entry, self)
        self._apply_dialog_style(dlg)
        if dlg.exec() == QDialog.Accepted:
            submit_entry(self._project_name, entry, dlg.summary)
            self._editor.clear()
            self._unsaved = False
            self._refresh_sidebar()
            self._show_toast("Successfully submitted! ^_^")

    def _on_view_summary(self):
        dlg = SummaryDialog(self._project_name, self)
        self._apply_dialog_style(dlg)
        dlg.exec()

    def _on_export(self):
        dlg = ExportDialog(self._project_name, self)
        self._apply_dialog_style(dlg)
        dlg.exec()

    def _on_settings(self):
        dlg = SettingsDialog(self._current_font, self)
        self._apply_dialog_style(dlg)
        if dlg.exec() == QDialog.Accepted:
            self._apply_font(dlg.chosen_font)

    def _on_feedback(self):
        import urllib.parse
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        subject = urllib.parse.quote("Onward Feedback")
        QDesktopServices.openUrl(QUrl(f"mailto:missing.sharpie404@passfwd.com?subject={subject}"))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _apply_dialog_style(self, dlg: QDialog):
        fo = FONT_OPTIONS[self._current_font]
        dlg.setStyleSheet(base_stylesheet(fo["family"], fo["size"]))

    def _show_toast(self, message: str):
        Toast(message, self.centralWidget())


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    os.makedirs(ONWARD_DIR, exist_ok=True)

    app = QApplication(sys.argv)
    app.setApplicationName("Onward")

    for family in ["Atkinson Hyperlegible", "Crimson Text", "Courier Prime"]:
        QFontDatabase.addApplicationFont(family)

    launch = LaunchWindow()
    app.launch = launch  # keep reference to prevent garbage collection
    launch.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
