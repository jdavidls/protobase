import os
from pathlib import Path
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, DirModifiedEvent


WATCH_DIRS = [Path("src"), Path("tests")]
WATCH_SUFFIXES = [
    ".py",
]


class Watcher(FileSystemEventHandler):
    """
    Monitors file system events and triggers actions accordingly.
    """

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent):
        if isinstance(event, FileModifiedEvent):
            filepath = Path(event.src_path)
            if not any(filepath.is_relative_to(wdir) for wdir in WATCH_DIRS):
                return
            if filepath.suffix not in WATCH_SUFFIXES:
                return

        run_tests()


def build_docs():
    """
    Runs the unit tests using the `unittest` module.
    """
    os.system("clear && printf '\\e[3J'")
    # subprocess.call("sphinx-apidoc -o docs/source src/protobase".split())
    subprocess.call("sphinx-build docs dist/docs".split())


def run_tests():
    """
    Runs the unit tests using the `unittest` module.
    """
    os.system("clear && printf '\\e[3J'")

    subprocess.call("python -m unittest discover -s tests".split())


def run_dev():
    """
    Run the unit tests when a file changes.
    """

    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()

    try:
        run_tests()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
