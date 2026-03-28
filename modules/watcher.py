import time
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from modules.scrubber import MetadataScrubber
from PySide6.QtCore import QObject, Signal

class ScrubberEventHandler(FileSystemEventHandler):
    def __init__(self, output_dir, spoof, preset, signals):
        super().__init__()
        self.output_dir = output_dir
        self.spoof = spoof
        self.preset = preset
        self.scrubber = MetadataScrubber()
        self.signals = signals

    def on_created(self, event):
        if not event.is_directory:
            # Wait briefly to ensure file is fully written before scrubbing
            time.sleep(1)
            
            input_path = Path(event.src_path)
            output_path = Path(self.output_dir) / f"scrubbed_{input_path.name}"
            
            try:
                result = self.scrubber.scrub(input_path, output_path, self.spoof, self.preset)
                if result.get('success'):
                    self.signals.file_processed.emit(f"Watch Folder: Scrubbed {input_path.name}")
                else:
                    self.signals.file_processed.emit(f"Watch Folder Error: {input_path.name} - {result.get('error')}")
            except Exception as e:
                self.signals.file_processed.emit(f"Watch Folder Exception: {str(e)}")

class WatcherSignals(QObject):
    file_processed = Signal(str)

class FolderWatcher:
    def __init__(self, watch_dir, output_dir, spoof=False, preset="None"):
        self.watch_dir = watch_dir
        self.output_dir = output_dir
        self.spoof = spoof
        self.preset = preset
        self.observer = None
        self.signals = WatcherSignals()

    def start(self):
        if self.observer is not None:
            return
            
        os.makedirs(self.watch_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        event_handler = ScrubberEventHandler(self.output_dir, self.spoof, self.preset, self.signals)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.watch_dir, recursive=False)
        self.observer.start()

    def stop(self):
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None
