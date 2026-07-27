# PDF/A Converter - Standard Pubblica Amministrazione

Applicazione desktop con interfaccia grafica (GUI) sviluppata in Python con PyQt6 e Ghostscript per convertire documenti PDF nello standard **PDF/A-1b** (e PDF/A-2b), raccomandato per la conservazione digitale a norma per la Pubblica Amministrazione.

Eseguibile e compatibile sia su **Linux** che su **Windows**.

---

## 🌟 Caratteristiche Principali

- 📄 **Interfaccia Pulita e Semplice**: Trascina e rilascia (Drag & Drop) qualsiasi file `.pdf` oppure selezionalo con il pulsante "Sfoglia".
- ⚙️ **Conversione PDF/A con Ghostscript**: Generazione automatica delle definizioni PostScript `PDFA_def.ps` e associazione dei profili colore ICC sRGB.
- 🔄 **Loader e Feedback in Tempo Reale**: Animazione durante l'elaborazione e log dettagliato in caso di errori.
- 📁 **Salvataggio Automatico**: Il file convertito viene salvato nella stessa cartella del file originale con il suffisso `-PdfA.pdf` (es. `documento.pdf` -> `documento-PdfA.pdf`).
- 🛠️ **Pannello Configurazione (Impostazioni)**:
  - Rilevamento automatico o manuale dell'eseguibile Ghostscript (`gs` / `gswin64c.exe`).
  - Rilevamento automatico o manuale del profilo colore sRGB ICC.
  - Selezione dello standard PDF/A (PDF/A-1b predefinito, PDF/A-2b).
  - Possibilità di aggiungere parametri Ghostscript extra.
  - Pulsante di test diagnostico per Ghostscript.

---

## 🚀 Requisiti di Sistema

- **Ghostscript** installato nel sistema:
  - **Linux**: Solitamente preinstallato o installabile con `sudo apt install ghostscript` / `sudo dnf install ghostscript`.
  - **Windows**: Scaricabile gratuitamente dal sito ufficiale [Ghostscript.com](https://ghostscript.com/releases/gsdnld.html) (es. `gswin64c.exe`).

---

## 💻 Installazione ed Esecuzione da Codice Sorgente

1. **Clona o scarica la repository**:
   ```bash
   git clone https://github.com/danielearrighi/pdf-a-convert
   cd pdf-a-convert
   ```

2. **Crea un ambiente virtuale ed installa le dipendenze**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Avvia l'applicazione**:
   ```bash
   python main.py
   ```

---

## 📦 Generazione dell'Eseguibile Standalone (.exe / Linux Binary)

Per creare un file eseguibile indipendente (che non richiede Python installato):

```bash
python build_exe.py
```

L'eseguibile compilato verrà generato nella cartella `dist/`:
- **Linux**: `dist/PDFA-Converter`
- **Windows**: `dist/PDFA-Converter.exe`

---

## 📐 Struttura del Progetto

```text
pdf-a-convert/
├── main.py                  # Entry point dell'applicazione
├── build_exe.py             # Script PyInstaller per la compilazione
├── requirements.txt         # Dipendenze Python (PyQt6, PyInstaller)
├── core/
│   ├── config.py            # Gestione impostazioni e QSettings
│   ├── converter.py         # Thread di background Ghostscript
│   ├── pdfa_def.py          # Generatore file PostScript PDFA_def.ps
│   └── utils.py             # Utility per ricerca gs, profili ICC e file manager
└── gui/
    ├── main_window.py       # Finestra principale dell'applicazione
    ├── drop_widget.py       # Area Drag & Drop file PDF
    ├── loader_widget.py     # Loader animato durante la conversione
    └── settings_dialog.py   # Finestra di configurazione dei percorsi
```
