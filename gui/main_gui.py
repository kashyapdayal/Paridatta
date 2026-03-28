import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QFileDialog, QMessageBox,
    QProgressBar, QGroupBox, QStatusBar, QListWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPainter, QColor, QPen

# Import core logic
sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.scrubber import MetadataScrubber

class ScrubberWorker(QThread):
    progress = Signal(int)
    finished_file = Signal(str, bool, str)
    all_done = Signal(int, int)

    def __init__(self, file_paths, output_dir):
        super().__init__()
        self.file_paths = file_paths
        self.output_dir = output_dir

    def run(self):
        scrubber = MetadataScrubber()
        success_count = 0
        fail_count = 0
        
        for i, path in enumerate(self.file_paths):
            try:
                input_path = Path(path)
                output_path = Path(self.output_dir) / input_path.name
                
                result = scrubber.scrub(input_path, output_path)
                
                if result.get("success", False):
                    success_count += 1
                    self.finished_file.emit(path, True, f"Scrubbed: {output_path.name}")
                else:
                    fail_count += 1
                    self.finished_file.emit(path, False, str(result.get("error", "Failed to scrub")))
            except Exception as e:
                fail_count += 1
                self.finished_file.emit(path, False, str(e))
            
            # Update progress
            progress_val = int(((i + 1) / len(self.file_paths)) * 100)
            self.progress.emit(progress_val)
            
        self.all_done.emit(success_count, fail_count)

class DragDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(QListWidget.ExtendedSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            # Visual feedback on drag enter
            self.setStyleSheet("QListWidget { background-color: #1e1e2e; border: 2px solid #a6e3a1; } QListWidget::item { padding: 8px; border-radius: 4px; }")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("") # Reset
        event.accept()

    def dropEvent(self, event):
        self.setStyleSheet("") # Reset
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if os.path.isfile(path) and not self.findItems(path, Qt.MatchExactly):
                self._add_styled_item(path)
            elif os.path.isdir(path):
                # Optionally handle directories
                for root, _, files in os.walk(path):
                    for f in files:
                        full_path = os.path.join(root, f)
                        if not self.findItems(full_path, Qt.MatchExactly):
                            self._add_styled_item(full_path)
        event.accept()

    def _add_styled_item(self, path):
        item = QListWidgetItem(path)
        item.setToolTip(path)
        self.addItem(item)

    def paintEvent(self, event):
        super().paintEvent(event)
        # Draw placeholder text when empty
        if self.count() == 0:
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.Antialiasing)
            pen = QPen(QColor("#6c7086"))
            painter.setPen(pen)
            
            font = painter.font()
            font.setPointSize(14)
            font.setBold(True)
            painter.setFont(font)
            
            text = "Drag & Drop Files or Folders Here\n\n(Supports large media files, docs, images instantly)"
            painter.drawText(self.viewport().rect(), Qt.AlignCenter, text)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paridatta - Universal File Metadata Scrubber")
        self.resize(850, 650)
        self.setMinimumSize(600, 400)
        
        self.apply_stylesheet()
        self.setup_ui()

    def apply_stylesheet(self):
        # Modern Catppuccin Mocha inspired dark theme
        qss = """
        QMainWindow {
            background-color: #11111b;
        }
        QWidget {
            background-color: #11111b;
            color: #cdd6f4;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }
        QLabel#headerTitle {
            font-size: 24px;
            font-weight: bold;
            color: #cba6f7;
        }
        QLabel#headerSub {
            font-size: 14px;
            color: #a6adc8;
            margin-bottom: 10px;
        }
        QGroupBox {
            border: 1px solid #45475a;
            border-radius: 8px;
            margin-top: 15px;
            font-weight: bold;
            color: #89b4fa;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            left: 10px;
        }
        QListWidget {
            background-color: #181825;
            border: 1px solid #313244;
            border-radius: 6px;
            padding: 5px;
            outline: none;
        }
        QListWidget::item {
            padding: 8px;
            border-radius: 4px;
            border-bottom: 1px solid #1e1e2e;
        }
        QListWidget::item:selected {
            background-color: #45475a;
            color: #cdd6f4;
        }
        QListWidget::item:hover {
            background-color: #313244;
        }
        QPushButton {
            background-color: #313244;
            border: none;
            border-radius: 6px;
            padding: 10px 16px;
            font-weight: bold;
            color: #cdd6f4;
        }
        QPushButton:hover {
            background-color: #45475a;
        }
        QPushButton:pressed {
            background-color: #585b70;
        }
        QPushButton#scrubButton {
            background-color: #a6e3a1;
            color: #11111b;
            font-size: 14px;
            padding: 10px 24px;
        }
        QPushButton#scrubButton:hover {
            background-color: #94cc90;
        }
        QPushButton#scrubButton:disabled {
            background-color: #45475a;
            color: #7f849c;
        }
        QProgressBar {
            border: 1px solid #313244;
            border-radius: 6px;
            text-align: center;
            background-color: #1e1e2e;
            color: #cdd6f4;
            font-weight: bold;
            height: 20px;
        }
        QProgressBar::chunk {
            background-color: #89b4fa;
            border-radius: 5px;
        }
        QStatusBar {
            background-color: #1e1e2e;
            color: #a6adc8;
            border-top: 1px solid #313244;
        }
        """
        self.setStyleSheet(qss)

    def setup_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 10)
        layout.setSpacing(15)
        
        # Header Area
        header_layout = QVBoxLayout()
        header_title = QLabel("Paridatta Scrubber")
        header_title.setObjectName("headerTitle")
        
        header_sub = QLabel("Absolute Privacy. Zero Metadata. Handles any file type or size.")
        header_sub.setObjectName("headerSub")
        
        header_layout.addWidget(header_title)
        header_layout.addWidget(header_sub)
        layout.addLayout(header_layout)
        
        # Files List Group
        group_box = QGroupBox("Target Files")
        group_layout = QVBoxLayout(group_box)
        group_layout.setContentsMargins(10, 20, 10, 10)
        
        self.file_list = DragDropListWidget()
        group_layout.addWidget(self.file_list)
        layout.addWidget(group_box)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("➕ Add Files")
        self.btn_add.clicked.connect(self.add_files)
        
        self.btn_remove_selected = QPushButton("➖ Remove Selected")
        self.btn_remove_selected.clicked.connect(self.remove_selected_files)

        self.btn_clear = QPushButton("🗑️ Clear All")
        self.btn_clear.clicked.connect(self.file_list.clear)
        
        self.btn_scrub = QPushButton("✨ Scrub Metadata")
        self.btn_scrub.setObjectName("scrubButton")
        self.btn_scrub.setCursor(Qt.PointingHandCursor)
        self.btn_scrub.clicked.connect(self.start_scrubbing)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove_selected)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_scrub)
        
        layout.addLayout(btn_layout)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% - Waiting...")
        layout.addWidget(self.progress_bar)
        
        self.setCentralWidget(main_widget)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Waiting for files...")

        # Update status based on list changes
        self.file_list.model().rowsInserted.connect(self.update_status_count)
        self.file_list.model().rowsRemoved.connect(self.update_status_count)

    def update_status_count(self):
        count = self.file_list.count()
        if count == 0:
            self.status_bar.showMessage("Ready. Waiting for files...")
        else:
            self.status_bar.showMessage(f"{count} file(s) loaded. Ready to scrub.")

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Scrub", "", "All Files (*)")
        for f in files:
            if not self.file_list.findItems(f, Qt.MatchExactly):
                self.file_list._add_styled_item(f)

    def remove_selected_files(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def start_scrubbing(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "No Files", "Please add files to scrub first.")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory for Cleaned Files")
        if not output_dir:
            return

        file_paths = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        
        self.btn_scrub.setEnabled(False)
        self.btn_add.setEnabled(False)
        self.btn_clear.setEnabled(False)
        self.btn_remove_selected.setEnabled(False)
        self.file_list.setEnabled(False)
        
        self.status_bar.showMessage("Scrubbing files (large videos may take time)...")
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Scrubbing... %p%")
        
        self.worker = ScrubberWorker(file_paths, output_dir)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished_file.connect(self.on_file_finished)
        self.worker.all_done.connect(self.on_all_done)
        self.worker.start()

    def on_file_finished(self, path, success, message):
        icon = "✅" if success else "❌"
        self.status_bar.showMessage(f"{icon} {Path(path).name}: {message}")

    def on_all_done(self, success_count, fail_count):
        self.btn_scrub.setEnabled(True)
        self.btn_add.setEnabled(True)
        self.btn_clear.setEnabled(True)
        self.btn_remove_selected.setEnabled(True)
        self.file_list.setEnabled(True)
        
        self.progress_bar.setFormat("Complete!")
        self.status_bar.showMessage(f"Done! Successfully scrubbed: {success_count} | Failed: {fail_count}")
        QMessageBox.information(self, "Scrubbing Complete", f"All files processed.\n\nSuccessfully Scrubbed: {success_count}\nFailed: {fail_count}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()