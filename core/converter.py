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
    Background worker thread to run Ghostscript PDF/A conversion on single or multiple files without blocking the GUI.
    """
    progress = pyqtSignal(str)
    progress_step = pyqtSignal(int, int, str)  # current_step (1-based), total_steps, status_text
    finished = pyqtSignal(bool, list, str)  # all_success, output_filepaths_list, log_or_error_message

    def __init__(
        self,
        input_files,
        gs_path: str,
        icc_path: str,
        pdfa_level: str = "1b",
        extra_args: str = "",
        output_suffix: str = "-pdfa",
        parent=None
    ):
        super().__init__(parent)
        if isinstance(input_files, str):
            self.input_files = [input_files] if input_files else []
        else:
            self.input_files = list(input_files) if input_files else []
            
        self.gs_path = gs_path
        self.icc_path = icc_path
        self.pdfa_level = pdfa_level
        self.extra_args = extra_args
        self.output_suffix = output_suffix or "-pdfa"

    def run(self):
        if not self.input_files:
            self.finished.emit(False, [], "Nessun file di input specificato.")
            return

        for file_path in self.input_files:
            if not file_path or not os.path.isfile(file_path):
                self.finished.emit(False, [], f"Il file di input non esiste o non è valido:\n{file_path}")
                return

        if not self.gs_path or not os.path.isfile(self.gs_path):
            self.finished.emit(
                False,
                [],
                f"Ghostscript non è stato trovato al percorso specificato:\n{self.gs_path}\nControlla le Impostazioni."
            )
            return

        total_files = len(self.input_files)
        successful_output_files = []
        all_logs = []
        overall_success = True

        with tempfile.TemporaryDirectory() as tmp_dir:
            ps_def_path = os.path.join(tmp_dir, "PDFA_def.ps")
            create_pdfa_def_ps(self.icc_path, ps_def_path, self.pdfa_level)
            pdfa_val = "2" if "2" in self.pdfa_level else "1"

            for idx, input_file in enumerate(self.input_files, start=1):
                input_path = Path(input_file)
                parent_dir = input_path.parent
                stem = input_path.stem
                output_file = str(parent_dir / f"{stem}{self.output_suffix}.pdf")

                status_msg = f"[{idx}/{total_files}] Conversione in corso: {input_path.name}"
                self.progress.emit(status_msg)
                self.progress_step.emit(idx - 1, total_files, status_msg)

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

                if self.icc_path and os.path.isfile(self.icc_path):
                    icc_path_ps = self.icc_path.replace("\\", "/")
                    cmd.append(f"--permit-file-read={icc_path_ps}")

                if self.extra_args.strip():
                    try:
                        extra_list = shlex.split(self.extra_args)
                        cmd.extend(extra_list)
                    except Exception:
                        pass

                cmd.append(ps_def_path)
                cmd.append(str(input_path))

                all_logs.append(f"=== Conversione File [{idx}/{total_files}]: {input_path.name} ===")

                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        universal_newlines=True,
                        env=get_clean_env()
                    )

                    file_logs = []
                    while True:
                        line = process.stdout.readline()
                        if not line and process.poll() is not None:
                            break
                        if line:
                            file_logs.append(line.strip())
                            if "Processing pages" in line or "Page " in line:
                                page_status = f"[{idx}/{total_files}] {input_path.name} - {line.strip()}"
                                self.progress.emit(page_status)
                                self.progress_step.emit(idx - 1, total_files, page_status)

                    return_code = process.wait()
                    all_logs.extend(file_logs)
                    all_logs.append("")

                    if return_code == 0 and os.path.isfile(output_file) and os.path.getsize(output_file) > 0:
                        successful_output_files.append(output_file)
                        self.progress_step.emit(idx, total_files, f"[{idx}/{total_files}] Completato: {input_path.name}")
                    else:
                        overall_success = False
                        if return_code != 0:
                            all_logs.append(f"ERRORE: Codice di uscita Ghostscript {return_code} per {input_path.name}")
                        else:
                            all_logs.append(f"ERRORE: Il file di output per {input_path.name} non è stato creato o è vuoto.")

                        if os.path.exists(output_file):
                            try:
                                os.remove(output_file)
                            except Exception as cleanup_err:
                                all_logs.append(f"Impossibile rimuovere il file non valido '{output_file}': {cleanup_err}")

                except Exception as e:
                    overall_success = False
                    all_logs.append(f"ECCEZIONE durante la conversione di {input_path.name}: {str(e)}")
                    if os.path.exists(output_file):
                        try:
                            os.remove(output_file)
                        except Exception as cleanup_err:
                            all_logs.append(f"Impossibile rimuovere il file non valido '{output_file}': {cleanup_err}")

        full_log = "\n".join(all_logs)

        if overall_success and len(successful_output_files) == total_files:
            self.progress.emit("Conversione completata con successo!")
            self.progress_step.emit(total_files, total_files, "Conversione completata con successo!")
            self.finished.emit(True, successful_output_files, full_log)
        else:
            err_msg = f"Conversione completata con errori ({len(successful_output_files)} di {total_files} file riusciti).\n\nLog:\n{full_log}"
            self.finished.emit(False, successful_output_files, err_msg)
