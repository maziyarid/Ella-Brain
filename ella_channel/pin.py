"""Explicit pin of the hardening branch. Not a merge."""

from __future__ import annotations

import hashlib
from pathlib import Path

# hardening/combined-no-overwrite-lock-timeout, not merged into this branch.
PIN_SHA = "d01d1f15f0048d3a5874b59fb6c0759e508c6539"
PIN_IO_SHA256 = "9787d2223cf4a69a9c7664eff3240d170e2b8992e33efc87b276d3216807c874"


def io_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_imported_io() -> str:
    """Refuse to run unless the imported ella_brain/_io.py is the pin."""

    import ella_brain._io as io_module

    path = Path(io_module.__file__).resolve()
    digest = io_digest(path)
    if digest != PIN_IO_SHA256:
        raise SystemExit(
            "ella_brain pin mismatch. This adapter requires "
            f"{PIN_SHA} (_io.py sha256 {PIN_IO_SHA256}). "
            f"Imported {path} sha256 {digest}. "
            "Set PYTHONPATH to a checkout of that commit. Do not copy _io.py into this branch."
        )
    return str(path)
