import json, os, sys, re
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple
from loguru import logger

# Path where settings live
DEFAULT_SETTINGS_PATH = Path(__file__).with_name("settings.json")

def load_settings() -> Dict:
    '''
    Load configuration from settings.json.
    Also configures logging globally (so all modules share same logger).
    '''
    for p in DEFAULT_SETTINGS_PATH:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            _setup_logging(cfg)
            logger.debug(f"Loaded settings from {p}")
            return cfg
    # If no config found, hard-exit: tool cannot run without defaults
    print("ERROR: No settings.json found", file=sys.stderr)
    sys.exit(2)

def _setup_logging(cfg: Dict):
    '''
    Configure loguru to log both stderr and a rotating file
    Settings come from JSON config
    '''
    log_dir = Path(cfg["logging"]["log_file"]).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.remove()     # Remove default log handler
    level = cfg["logging"].get("log_level", "INFO").upper()
    # Log to console
    logger.add(sys.stderr, level=level)
    # Log to rotating file (2 MB chunks, keep 10 files)
    logger.add(cfg["logging"]["log_file"], level=level, rotation="2 MB", retention="10 files")

def ensure_output_path(in_path: Path, outdir: Optional[str], new_ext: str, overwrite: bool, suffix: str) -> Path:
    '''
    Build a safe output path for converted file
    - If outdir is provided, use that; else keep alongside input.
    - If overwrite = False and the file exists, append suffix like (1).
    '''
    if outdir:
        base = Path(outdir)
    else:
        base = in_path.parent
    base.mkdir(parents=True, exist_ok=True)

    stem = in_path.stem
    candidate = base / f"{stem}{new_ext}"

    if overwrite or not candidate.exists():
        return candidate
    
    # If file exists and overwrite is disabled, keep bumping suffix
    i = 1
    while True:
        candidate = base / f"{stem} {suffix.replace(')', f'-{i})')}{new_ext}" if suffix.endswith(')') else f"{stem}{suffix}-{i}{new_ext}"
        if not candidate.exists():
            return candidate
        i += 1

def iter_target_files(root: Path, recursive: bool, exts: Iterable[str]) -> Iterable[Path]:
    '''
    Yield all files matching given extensions from a root path.
    - If root is a file, yield it directly.
    - If root is a folder, search either shallow or recursive.
    '''
    exts = {e.lower() for e in exts}
    if root.is_file():
        if root.suffix.lower() in exts: 
            yield root
        return
    pattern = "**/*" if recursive else "*"
    for p in root.glob(pattern):
        if p.is_file() and p.suffix.lower() in exts:
            yield p

def is_windows() -> bool:
    '''
    Simple helper to check if we're on windows (needed for docx2pdf).
    '''
    return os.name == "nt"


        