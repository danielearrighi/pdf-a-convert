import os

def create_pdfa_def_ps(icc_path: str, output_ps_path: str, pdfa_level: str = "1b") -> str:
    """
    Generates a PDFA_def.ps PostScript preamble file required by Ghostscript for PDF/A conversion.
    """
    icc_path_ps = icc_path.replace("\\", "/") if icc_path else ""
    
    is_pdfa1 = "1" in pdfa_level
    pdfa_title = "sRGB IEC61966-2.1"
    pdfa_key = "/GTS_PDFA1" if is_pdfa1 else "/GTS_PDFA2"
    
    if icc_path_ps and os.path.isfile(icc_path):
        content = f"""% Definition of OutputIntent for PDF/A
/ICCProfile ({icc_path_ps}) def

[/_objdef {{icc_PDFA}} /type /stream /OBJ pdfmark
[{{icc_PDFA}} << /N 3 /Filter /FlateDecode >> /PUT pdfmark
[{{icc_PDFA}} ICCProfile (r) file /PUT pdfmark

[{pdfa_key} /Title ({pdfa_title}) /OutputConditionIdentifier (sRGB) /DestOutputProfile {{icc_PDFA}} /PDFMark /OutputIntent pdfmark
"""
    else:
        content = f"""% Definition of OutputIntent for PDF/A (Default)
[{pdfa_key} /Title ({pdfa_title}) /OutputConditionIdentifier (sRGB) /PDFMark /OutputIntent pdfmark
"""

    with open(output_ps_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_ps_path
