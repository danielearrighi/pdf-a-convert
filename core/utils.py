import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def find_ghostscript_executable() -> str:
    """Find Ghostscript binary on the system (Linux / Windows / macOS)."""
    system = platform.system().lower()
    
    # 1. Search PATH
    executables = ["gs", "gswin64c.exe", "gswin32c.exe", "gsc.exe"]
    for exe in executables:
        found = shutil.which(exe)
        if found:
            return found

    # 2. Check standard system locations on Windows
    if system == "windows":
        possible_dirs = [
            r"C:\Program Files\gs",
            r"C:\Program Files (x86)\gs"
        ]
        for base_dir in possible_dirs:
            if os.path.exists(base_dir):
                for sub in sorted(os.listdir(base_dir), reverse=True):
                    bin_path = os.path.join(base_dir, sub, "bin")
                    for exe_name in ["gswin64c.exe", "gswin32c.exe", "gsc.exe"]:
                        full_path = os.path.join(bin_path, exe_name)
                        if os.path.isfile(full_path):
                            return full_path

    # 3. Check standard Linux/Unix locations
    elif system in ["linux", "darwin"]:
        common_paths = [
            "/usr/bin/gs",
            "/usr/local/bin/gs",
            "/opt/homebrew/bin/gs"
        ]
        for p in common_paths:
            if os.path.isfile(p) and os.access(p, os.X_OK):
                return p

    return ""

def find_system_icc_profile() -> str:
    """Locate standard sRGB ICC profile on the system."""
    system = platform.system().lower()
    candidates = []

    if system == "linux":
        candidates = [
            "/usr/share/color/icc/colord/sRGB.icc",
            "/usr/share/color/icc/sRGB.icc",
            "/usr/share/ghostscript/iccprofiles/default_rgb.icc",
            "/usr/share/ghostscript/10.03.1/iccprofiles/default_rgb.icc",
            "/usr/share/ghostscript/9.55.0/iccprofiles/default_rgb.icc",
            "/usr/share/color/icc/ghostscript/default_rgb.icc"
        ]
        # Also check wildcard ghostscript dir
        gs_icc_base = "/usr/share/ghostscript"
        if os.path.exists(gs_icc_base):
            for root, dirs, files in os.walk(gs_icc_base):
                for f in files:
                    if f.lower() in ["default_rgb.icc", "srgb.icc", "srgb.icm"]:
                        candidates.append(os.path.join(root, f))

    elif system == "windows":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        color_dir = os.path.join(windir, "System32", "spool", "drivers", "color")
        candidates = [
            os.path.join(color_dir, "sRGB Color Space Profile.icm"),
            os.path.join(color_dir, "sRGB.icm"),
            os.path.join(color_dir, "sRGB.icc")
        ]

    for path in candidates:
        if os.path.isfile(path):
            return path

    return ""

def get_clean_env() -> dict:
    """
    Returns a copy of os.environ with PyInstaller's library path and Qt overrides removed.
    This prevents child processes (like Ghostscript, xdg-open, kde-open, etc.) from loading
    bundled PyInstaller shared libraries or Qt plugins instead of system ones.
    """
    env = os.environ.copy()
    meipass = str(getattr(sys, "_MEIPASS", ""))

    # 1. Clean LD_LIBRARY_PATH
    if "LD_LIBRARY_PATH_ORIG" in env:
        orig = env.get("LD_LIBRARY_PATH_ORIG")
        if orig:
            env["LD_LIBRARY_PATH"] = orig
        else:
            env.pop("LD_LIBRARY_PATH", None)
    elif meipass:
        ld_path = env.get("LD_LIBRARY_PATH", "")
        paths = [p for p in ld_path.split(":") if p and meipass not in p]
        if paths:
            env["LD_LIBRARY_PATH"] = ":".join(paths)
        else:
            env.pop("LD_LIBRARY_PATH", None)

    # 2. Clean Qt-specific environment variables set by PyInstaller / PyQt
    qt_vars = ["QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH", "QT_QPA_PLATFORM", "QT_QPA_PLATFORMTHEME"]
    for var in qt_vars:
        orig_key = f"{var}_ORIG"
        if orig_key in env:
            orig_val = env.get(orig_key)
            if orig_val:
                env[var] = orig_val
            else:
                env.pop(var, None)
        elif meipass and var in env:
            val = env[var]
            if meipass in val:
                paths = [p for p in val.split(":") if p and meipass not in p]
                if paths:
                    env[var] = ":".join(paths)
                else:
                    env.pop(var, None)
        elif meipass:
            # In frozen mode, if QT_PLUGIN_PATH or QT_QPA_PLATFORM_PLUGIN_PATH are set, remove them for child process
            if var in ["QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH"]:
                env.pop(var, None)

    # 3. Clean Python environment variables if in frozen mode or containing _MEIPASS
    for py_var in ["PYTHONPATH", "PYTHONHOME"]:
        if meipass and py_var in env:
            env.pop(py_var, None)

    return env

def open_file(path: str):
    """Open a file using the system default application."""
    if not os.path.exists(path) or not os.path.isfile(path):
        return
        
    system = platform.system().lower()
    clean_env = get_clean_env()
    try:
        if system == "windows":
            os.startfile(path)
        elif system == "darwin":
            subprocess.Popen(["open", path], env=clean_env)
        else: # linux
            subprocess.Popen(["xdg-open", path], env=clean_env)
    except Exception:
        pass

def open_folder(path: str):
    """Open the parent folder of a file (or the folder itself) in the system file manager."""
    if not os.path.exists(path):
        return
        
    system = platform.system().lower()
    folder = path if os.path.isdir(path) else os.path.dirname(path)
    clean_env = get_clean_env()
    
    try:
        if system == "windows":
            if os.path.isfile(path):
                subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
            else:
                os.startfile(folder)
        elif system == "darwin":
            if os.path.isfile(path):
                subprocess.Popen(["open", "-R", path], env=clean_env)
            else:
                subprocess.Popen(["open", path], env=clean_env)
        else: # linux
            subprocess.Popen(["xdg-open", folder], env=clean_env)
    except Exception:
        pass

def open_file_or_folder(path: str):
    """Open a file in default application if it is a file, or open folder if it is a directory."""
    if os.path.isfile(path):
        open_file(path)
    else:
        open_folder(path)

def get_asset_path(filename: str) -> str:
    """Get absolute path to a resource asset, working both for dev mode and PyInstaller frozen executable."""
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(getattr(sys, "_MEIPASS"))
    else:
        base_path = Path(__file__).resolve().parent.parent
    asset_file = base_path / "assets" / filename
    return str(asset_file)

def register_desktop_entry_linux():
    """On Linux/Wayland, create a desktop entry in ~/.local/share/applications so taskbar & app launcher show custom icon."""
    if platform.system().lower() != "linux":
        return

    desktop_dir = Path.home() / ".local" / "share" / "applications"
    desktop_file = desktop_dir / "pdfa-converter.desktop"
    
    icon_path = get_asset_path("app_icon.png")
    if not os.path.exists(icon_path):
        return

    python_exe = sys.executable
    main_script = Path(__file__).resolve().parent.parent / "main.py"

    content = f"""[Desktop Entry]
Type=Application
Name=PDF/A Converter PA
Comment=Conversione PDF/A per la Pubblica Amministrazione
Exec={python_exe} {main_script}
Icon={icon_path}
Terminal=false
Categories=Utility;Office;
StartupWMClass=pdfa-converter
"""
    try:
        desktop_dir.mkdir(parents=True, exist_ok=True)
        desktop_file.write_text(content, encoding="utf-8")
    except Exception:
        pass


