from pathlib import Path
from loguru import logger
from typing import Dict
from .ocr_utils import pdf_has_searchable_text, ocr_searchable_pdf

def convert_pdf_to_docx(in_pdf: Path, out_docx: Path, cfg: Dict):
    '''
    Convert a single PDF into DOCX
    Steps:
    1. If PDF has no selectable text and auto_ocr is enabled -> run OCR first.
    2. Use pdf2docx.Converter to create the DOCX.
    Returns 
    '''
    from pdf2docx import Converter

    # Decide whether to OCR
    use_ocr = cfg["pdf2docx"].get("auto_ocr_if_scanned", True)
    if use_ocr and not pdf_has_searchable_text(in_pdf):
        lang = cfg["pdf2docx"].get("ocr_language", "eng")
        dpi = cfg["pdf2docx"].get("ocr_dpi", 300)
        ocred = ocr_searchable_pdf(in_pdf, lang, dpi)
        if ocred is not None:
            src = ocred
        else:
            logger.warning("Processing without OCR; output may be image-only in DOCX")
    
    try:
        # Perform the actual convversion
        layout_mode = cfg["pdf2docx"].get("layout_mode", "layout")
        max_pages = cfg["pdf2docx"].get("max_pages", 0)

        cv =  Converter(str(src))
        if max_pages and max_pages > 0:
            cv.convert(str(out_docx), start=0, end=max_pages)
        else:
            cv.convert(str(out_docx))
        cv.close()

        logger.success(f"Wrote {out_docx}")
        return True
    except Exception as e:
        logger.exception(f"Failed to convert PDF -> DOCX: {in_pdf} -> {out_docx}: {e}")
        return False