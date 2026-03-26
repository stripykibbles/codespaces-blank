import sys
import io
import csv
import os
import re
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QDialog, QComboBox, QFileDialog,
    QSizePolicy, QFrame, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QFontDatabase, QCloseEvent


# ── Constants ────────────────────────────────────────────────────────────────

FIELDNAMES = ["date", "time", "entry", "entry_word_count", "summary"]
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "novel.csv")
TXT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "novel.txt")

FONT_OPTIONS = {
    "Sans Serif":  {"family": "Atkinson Hyperlegible",  "size": 14},
    "Serif":       {"family": "Crimson Text",            "size": 15},
    "Monospace":   {"family": "Courier Prime",           "size": 13},
}

# Neutral light palette matching the original Streamlit aesthetic
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


# ── Pure logic (unchanged from original) ─────────────────────────────────────

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


def get_word_count() -> int:
    count = 0
    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                count += int(row["entry_word_count"])
    except FileNotFoundError:
        pass
    return count


def submit_entry(entry: str, summary: str):
    date, time = date_parse(datetime.now())
    word_count  = len(entry.split())
    row = {"date": date, "time": time, "entry": entry,
           "entry_word_count": word_count, "summary": summary}
    new_file = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def export_text() -> str:
    novel = ""
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            novel += row["entry"] + "\n\n"
    with open(TXT_PATH, "w", encoding="utf-8") as f:
        f.write(novel)
    return novel


def load_summaries() -> list[tuple[str, str]]:
    """Return list of (formatted_date, summary) in reverse chronological order."""
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append((row["date"], row["summary"]))
    rows.sort(key=lambda r: r[0], reverse=True)
    return [(date_format(d), s) for d, s in rows]


def import_csv_file(path: str) -> str | None:
    """Import a CSV file. Returns error string or None on success."""
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or list(reader.fieldnames) != FIELDNAMES:
            return "CSV file is not in a valid format."
        rows = list(reader)

    new_file = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if new_file:
            writer.writeheader()
        writer.writerows(rows)
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


# ── Dialogs ───────────────────────────────────────────────────────────────────

class SummaryDialog(QDialog):
    """Shows all entry summaries in reverse chronological order."""

    def __init__(self, parent=None):
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
            entries = load_summaries()
        except FileNotFoundError:
            entries = []

        if not entries:
            lbl = QLabel("A summary of your novel will go here!")
            lbl.setProperty("class", "dialog-body")
            lbl.setWordWrap(True)
            inner_layout.addWidget(lbl)
        else:
            for fmt_date, summary_text in entries:
                # Date chip
                date_lbl = QLabel(fmt_date)
                date_lbl.setObjectName("muted")
                date_lbl.setStyleSheet(
                    f"background-color: {PALETTE['border']}; "
                    f"color: {PALETTE['muted']}; "
                    "padding: 2px 8px; "
                    "font-size: 10pt;"
                )
                inner_layout.addWidget(date_lbl)

                # Summary text with left border
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

        self.text_edit = QTextEdit()
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

    def __init__(self, parent=None):
        super().__init__(parent)
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
        dest, _ = QFileDialog.getSaveFileName(self, "Save Text File", "novel.txt", "Text Files (*.txt)")
        if dest:
            text = export_text()
            with open(dest, "w", encoding="utf-8") as f:
                f.write(text)
            QMessageBox.information(self, "Exported", f"Text saved to:\n{dest}")

    def _export_csv(self):
        dest, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "novel.csv", "CSV Files (*.csv)")
        if dest:
            import shutil
            shutil.copy2(CSV_PATH, dest)
            QMessageBox.information(self, "Exported", f"CSV saved to:\n{dest}")


class ImportDialog(QDialog):
    """Import TXT or CSV."""

    def __init__(self, has_existing_content: bool, parent=None):
        super().__init__(parent)
        self.imported_text = None   # set if TXT imported
        self.imported_csv  = False  # set True if CSV imported successfully
        self.setWindowTitle("Import Work")
        self.setFixedSize(320, 150)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        if has_existing_content:
            warn = QLabel("⚠ Importing will overwrite your current entry.")
            warn.setStyleSheet(f"color: {PALETTE['muted']}; font-size: 10pt;")
            warn.setWordWrap(True)
            layout.addWidget(warn)

        txt_btn = QPushButton("Import Text File (.txt)")
        txt_btn.setProperty("class", "dialog-btn")
        txt_btn.clicked.connect(self._import_txt)

        csv_btn = QPushButton("Import CSV File (.csv)")
        csv_btn.setProperty("class", "dialog-btn")
        csv_btn.clicked.connect(self._import_csv)

        layout.addWidget(txt_btn)
        layout.addWidget(csv_btn)

        close_btn = QPushButton("Close")
        close_btn.setProperty("class", "dialog-btn")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)

    def _import_txt(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.imported_text = f.read()
            self.accept()

    def _import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if path:
            error = import_csv_file(path)
            if error:
                QMessageBox.warning(self, "Import Error", error)
            else:
                self.imported_csv = True
                self.accept()


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

        from PySide6.QtCore import QTimer
        QTimer.singleShot(2500, self.deleteLater)

    def _reposition(self, parent: QWidget):
        pw = parent.width()
        ph = parent.height()
        self.adjustSize()
        x = pw - self.width() - 20
        y = ph - self.height() - 20
        self.move(x, y)
        self.raise_()


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Typewriter")
        self.setMinimumSize(WINDOW_MIN_W, WINDOW_MIN_H)
        self._current_font = "Sans Serif"
        self._unsaved = False

        self._build_ui()
        self._apply_font(self._current_font)
        self._refresh_sidebar()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self._sidebar_widget = QWidget()
        self._sidebar_widget.setObjectName("sidebar")
        self._sidebar_widget.setFixedWidth(SIDEBAR_WIDTH)
        sidebar_layout = QVBoxLayout(self._sidebar_widget)
        sidebar_layout.setContentsMargins(14, 20, 14, 20)
        sidebar_layout.setSpacing(8)

        self._word_count_lbl = QLabel()
        self._word_count_lbl.setObjectName("wordCountLabel")
        self._word_count_lbl.setWordWrap(True)
        sidebar_layout.addWidget(self._word_count_lbl)

        sidebar_layout.addSpacing(6)

        self._btn_submit   = self._sidebar_button("Submit && Clear")
        self._btn_view     = self._sidebar_button("View Summary")
        self._btn_export   = self._sidebar_button("Export Work")
        self._btn_import   = self._sidebar_button("Import Work")
        self._btn_settings = self._sidebar_button("Settings")

        for btn in [self._btn_submit, self._btn_view, self._btn_export,
                    self._btn_import, self._btn_settings]:
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        self._btn_submit.clicked.connect(self._on_submit)
        self._btn_view.clicked.connect(self._on_view_summary)
        self._btn_export.clicked.connect(self._on_export)
        self._btn_import.clicked.connect(self._on_import)
        self._btn_settings.clicked.connect(self._on_settings)

        # Main writing area
        main_area = QWidget()
        main_area.setObjectName("mainArea")
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(40, 30, 40, 30)

        self._editor = QTextEdit()
        self._editor.setObjectName("editor")
        self._editor.setPlaceholderText("It was a dark and stormy night...")
        self._editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._editor.textChanged.connect(self._on_text_changed)
        main_layout.addWidget(self._editor)

        root.addWidget(self._sidebar_widget)
        root.addWidget(main_area, stretch=1)

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

    # ── Sidebar state ─────────────────────────────────────────────────────────

    def _refresh_sidebar(self):
        count = get_word_count()
        if count == 0:
            msg = "You've submitted 0 words.\n(It's going to be great.)"
        elif count == 1:
            msg = "You've submitted 1 word.\n(And it's a great start.)"
        else:
            msg = f"You've submitted {count} words.\n(And they're all amazing.)"
        self._word_count_lbl.setText(msg)

        has_csv = os.path.exists(CSV_PATH)
        self._btn_view.setVisible(has_csv)
        self._btn_export.setVisible(has_csv)
        self._btn_import.setVisible(not has_csv)

    # ── Unsaved-changes guard ─────────────────────────────────────────────────

    def _on_text_changed(self):
        self._unsaved = bool(self._editor.toPlainText())

    def closeEvent(self, event: QCloseEvent):
        if self._unsaved:
            reply = QMessageBox.question(
                self, "Unsaved Entry",
                "You have an unsaved entry. Are you sure you want to quit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
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
            submit_entry(entry, dlg.summary)
            self._editor.clear()
            self._unsaved = False
            self._refresh_sidebar()
            self._show_toast("Successfully submitted! ^_^")

    def _on_view_summary(self):
        dlg = SummaryDialog(self)
        self._apply_dialog_style(dlg)
        dlg.exec()

    def _on_export(self):
        dlg = ExportDialog(self)
        self._apply_dialog_style(dlg)
        dlg.exec()

    def _on_import(self):
        has_content = bool(self._editor.toPlainText().strip())
        dlg = ImportDialog(has_content, self)
        self._apply_dialog_style(dlg)
        if dlg.exec() == QDialog.Accepted:
            if dlg.imported_text is not None:
                self._editor.setPlainText(dlg.imported_text)
                self._unsaved = True
                self._show_toast("File imported! Keep writing.")
            elif dlg.imported_csv:
                self._refresh_sidebar()
                self._show_toast("CSV imported successfully! ^_^")

    def _on_settings(self):
        dlg = SettingsDialog(self._current_font, self)
        self._apply_dialog_style(dlg)
        if dlg.exec() == QDialog.Accepted:
            self._apply_font(dlg.chosen_font)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _apply_dialog_style(self, dlg: QDialog):
        fo = FONT_OPTIONS[self._current_font]
        dlg.setStyleSheet(base_stylesheet(fo["family"], fo["size"]))

    def _show_toast(self, message: str):
        Toast(message, self.centralWidget())


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Typewriter")

    # Attempt to load bundled/system fonts (best-effort)
    for family in ["Atkinson Hyperlegible", "Crimson Text", "Courier Prime"]:
        QFontDatabase.addApplicationFont(family)

    window = MainWindow()
    window.resize(1000, 680)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()