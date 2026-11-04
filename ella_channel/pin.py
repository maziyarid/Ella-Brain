"""Content pin for the hardened gate in this repository.

Main 9132753e4be980c75269be6de2658134e4960208 is the merged baseline.
Its ella_brain/_io.py and ella_brain/_stages.py bytes match the reviewed
hardening commit d01d1f15f0048d3a5874b59fb6c0759e508c6539. This module
checks both imported files. A hash of _io.py alone does not establish
_stages.py. There is no second checkout and no external PYTHONPATH.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

BASELINE_SHA = "9132753e4be980c75269be6de2658134e4960208"
PIN_IO_SHA256 = "9787d2223cf4a69a9c7664eff3240d170e2b8992e33efc87b276d3216807c874"
PIN_STAGES_SHA256 = "afc5ca45a8ee15d7b6aef7a19e2131800a910572ead847d6622ef069abb4133e"

_EXPECTED = {
    "ella_brain/_io.py": PIN_IO_SHA256,
    "ella_brain/_stages.py": PIN_STAGES_SHA256,
}


def verify_imported_gate() -> dict[str, str]:
    """Refuse to start unless both hardened files are the ones imported."""

    import ella_brain._io as io_module
    import ella_brain._stages as stages_module

    modules = {
        "ella_brain/_io.py": io_module,
        "ella_brain/_stages.py": stages_module,
    }
    found: dict[str, str] = {}
    mismatches: list[str] = []
    for label, module in modules.items():
        path = Path(module.__file__).resolve()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        found[label] = digest
        expected = _EXPECTED[label]
        if digest != expected:
            mismatches.append(
                f"{label} imported from {path} sha256 {digest}, expected {expected}"
            )
    if mismatches:
        raise SystemExit(
            "ella_brain pin mismatch against baseline "
            f"{BASELINE_SHA}. " + "; ".join(mismatches) + ". "
            "Use this repository's ella_brain. Do not point PYTHONPATH at another checkout."
        )
    return found
