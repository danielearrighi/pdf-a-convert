import os
import shlex
import tempfile
import subprocess
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from core.pdfa_def import create_pdfa_def_ps
from core.utils import get_clean_env

class PDFConverterThread(QThread):
    """
    Background worker thread to run Ghostscript PDF/A conversion without blocking the GUI.
    """
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str, str)  # success, output_filepath, log_or_error_message

    def __init__(
        self,
        input_file: str,
        gs_path: str,
        icc_path: str,
        pdfa_level: str = "1b",
        extra_args: str = "",
        parent=None
    ):
        super().__init__(parent)
        self.input_file = input_file
        self.gs_path = gs_path
        self.icc_path = icc_path
        self.pdfa_level = pdfa_level
        self.extra_args = extra_args

    def run(self):
        if not self.input_file or not os.path.isfile(self.input_file):
            self.finished.emit(False, "", "Il file di input non esiste o non è valido.")
            return

        if not self.gs_path or not os.path.isfile(self.gs_path):
            self.finished.emit(
                False,
                "",
                f"Ghostscript non è stato trovato al percorso specificato:\n{self.gs_path}\nControlla le Impostazioni."
            )
            return

        # Calculate output path: <original_name>-PdfA.pdf in same folder
        input_path = Path(self.input_file)
        parent_dir = input_path.parent
        stem = input_path.stem
        output_file = str(parent_dir / f"{stem}-PdfA.pdf")

        self.progress.emit("Preparazione del profilo di conversione PostScript...")

        # Create temp directory for temporary PDFA_def.ps
        with tempfile.TemporaryDirectory() as tmp_dir:
            ps_def_path = os.path.join(tmp_dir, "PDFA_def.ps")
            create_pdfa_def_ps(self.icc_path, ps_def_path, self.pdfa_level)

            pdfa_val = "2" if "2" in self.pdfa_level else "1"
            
            cmd = [
                self.gs_path,
                f"-dPDFA={pdfa_val}",
                "-dBATCH",
                "-dNOPAUSE",
                "-dNOOUTERSAVE",
                "-sColorConversionStrategy=UseDeviceIndependentColor",
                "-sProcessColorModel=DeviceRGB",
                "-sDEVICE=pdfwrite",
                "-dPDFACompatibilityPolicy=1",
                f"-sOutputFile={output_file}",
            ]

            # Append extra Ghostscript args if provided
            if self.extra_args.strip():
                try:
                    extra_list = shlex.split(self.extra_args)
                    cmd.extend(extra_list)
                except Exception:
                    pass

            cmd.append(ps_def_path)
            cmd.append(str(input_path))

            self.progress.emit("Esecuzione di Ghostscript per la conversione in PDF/A...")

            try:
                # Start process capturing stdout and stderr with cleaned environment
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    universal_newlines=True,
                    env=get_clean_env()
                )

                output_logs = []
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        output_logs.append(line.strip())
                        if "Processing pages" in line or "Page " in line:
                            self.progress.emit(f"Elaborazione: {line.strip()}")

                return_code = process.wait()

                full_log = "\n".join(output_logs)

                if return_code == 0 and os.path.isfile(output_file):
                    self.progress.emit("Conversione completata con successo!")
                    self.finished.emit(True, output_file, full_log)
                else:
                    err_msg = f"Ghostscript è terminato con codice di errore {return_code}.\n\nLog:\n{full_log}"
                    self.finished.emit(False, "", err_msg)

            except Exception as e:
                self.finished.emit(False, "", f"Errore durante l'esecuzione: {str(e)}")
