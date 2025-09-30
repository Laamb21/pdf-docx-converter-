from pathlib import Path
from typing import Optional
from loguru import logger
from pypdf import PdfReader
import subprocess
import shutil
import tempfile

def pdf_has_searchable_text(pdf_path: Path) -> bool:
    '''
    Quick probe: check first few pages to see if the PDF has real text.
    If not, most likely a scanned image (needs OCR).
    '''
    try:
        reader = PdfReader(str(pdf_path))
        for page in reader.pages[:5]:    # only sample first 5 pages
            text = page.extract_text() or ""
            if text.strip():
                return True
        return False
    except Exception as e:
        logger.warning(f"Failed to probe text in {pdf_path}: {e}")
        return False
    
def ocr_searchable_pdf(in_pdf: Path, lang: str = "eng", dpi: int = 300) -> Optional[Path]:
    '''
    Use ocrmypdf to generate a temporary searchable PDF from a scanned one.
    Returns path to the new file, or None if failure
    '''
    if shutil.which("ocrmypdf") is None:
        logger.warning("ocrmypdf not found on PATH. Skipping OCR.")
        return None
    
    # Create a throwaway temp folder for the OCR output 
    tmpdir = Path(tempfile.mkdtemp(prefix="ocr_"))
    out_pdf = tmpdir / "ocr.pdf"

    cmd = [
        "ocrmypdf",
        "--optimize", "0",
        "--skip-text", 
        "--output-type",  "pdf",
        "--image-dpi", str(dpi),
        "-l", lang,
        str(in_pdf),
        str(out_pdf),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return out_pdf
    except Exception as e:
        logger.error(f"OCR failed for {in_pdf}: {e.stderr.decode(errors='ignore')}")
        return None
    
    