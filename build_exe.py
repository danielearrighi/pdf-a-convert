import sys
import subprocess
from pathlib import Path

def build():
    print("=== Compilazione Eseguibile PDF/A Converter con PyInstaller ===")

    # Su Windows PyInstaller richiede un .ico per generare l'icona dell'eseguibile/taskbar;
    # un .png viene ignorato silenziosamente e resta l'icona di default di Python.
    icon_path = "assets/app_icon.ico" if sys.platform == "win32" else "assets/app_icon.png"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed", # Hide console window
        "--onefile",  # Create single standalone executable
        "--name", "PDFA-Converter",
        "--add-data", "assets:assets",
        "--icon", icon_path,
        "main.py"
    ]
    
    print("Esecuzione comando PyInstaller:", " ".join(cmd))
    res = subprocess.run(cmd)
    
    if res.returncode == 0:
        dist_dir = Path("dist").resolve()
        print("\n✅ Compilazione completata con successo!")
        print(f"L'eseguibile è disponibile nella cartella: {dist_dir}")
    else:
        print(f"\n❌ Errore durante la compilazione (Codice: {res.returncode})")

if __name__ == "__main__":
    build()
