import os
import sys
import subprocess
import shutil

def run_command(cmd):
    print(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)

def build_app():
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])

    separator = os.pathsep
    
    # Common PyInstaller arguments
    # --windowed: Do not show console when running the GUI
    # --noconfirm: Replace output directory without asking
    # --name: Name of the output executable
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--windowed",
        "--name=Paridatta",
        "--add-data=modules{sep}modules".format(sep=separator),
        "--add-data=gui{sep}gui".format(sep=separator),
        "--add-data=config.py{sep}.".format(sep=separator),
        "paridatta.py",
    ]

    print("Building Paridatta for the current platform...")
    run_command(cmd)

    print("=" * 60)
    if sys.platform == "win32":
        dist_path = os.path.join("dist", "Paridatta.exe")
        print(f"Build complete! Your Windows executable is located at: {dist_path}")
    elif sys.platform == "darwin":
        dist_path = os.path.join("dist", "Paridatta.app")
        print(f"Build complete! Your macOS application is located at: {dist_path}")
    else:
        dist_path = os.path.join("dist", "Paridatta")
        print(f"Build complete! Your Linux executable is located at: {dist_path}")

if __name__ == "__main__":
    build_app()
