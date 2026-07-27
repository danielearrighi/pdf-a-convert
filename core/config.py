from PyQt6.QtCore import QSettings
from core.utils import find_ghostscript_executable, find_system_icc_profile

class ConfigManager:
    """Manages application persistent settings using QSettings."""
    
    ORGANIZATION_NAME = "PDFAConvert"
    APPLICATION_NAME = "PDFAConverterTool"

    def __init__(self):
        self.settings = QSettings(self.ORGANIZATION_NAME, self.APPLICATION_NAME)

    @property
    def ghostscript_path(self) -> str:
        saved = self.settings.value("ghostscript_path", type=str)
        if saved:
            return saved
        detected = find_ghostscript_executable()
        return detected

    @ghostscript_path.setter
    def ghostscript_path(self, val: str):
        self.settings.setValue("ghostscript_path", val)

    @property
    def icc_profile_path(self) -> str:
        saved = self.settings.value("icc_profile_path", type=str)
        if saved:
            return saved
        detected = find_system_icc_profile()
        return detected

    @icc_profile_path.setter
    def icc_profile_path(self, val: str):
        self.settings.setValue("icc_profile_path", val)

    @property
    def pdfa_level(self) -> str:
        return self.settings.value("pdfa_level", "1b", type=str)

    @pdfa_level.setter
    def pdfa_level(self, val: str):
        self.settings.setValue("pdfa_level", val)

    @property
    def extra_gs_args(self) -> str:
        return self.settings.value("extra_gs_args", "", type=str)

    @extra_gs_args.setter
    def extra_gs_args(self, val: str):
        self.settings.setValue("extra_gs_args", val)

    @property
    def auto_open_folder(self) -> bool:
        return self.settings.value("auto_open_folder", False, type=bool)

    @auto_open_folder.setter
    def auto_open_folder(self, val: bool):
        self.settings.setValue("auto_open_folder", val)

    @property
    def theme(self) -> str:
        return self.settings.value("theme", "light", type=str)

    @theme.setter
    def theme(self, val: str):
        self.settings.setValue("theme", val)

    def reset_to_defaults(self):
        self.settings.clear()
