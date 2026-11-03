"""No-overwrite publication for version files."""

import os
from pathlib import Path

import pytest

from ella_brain._io import atomic_write
from ella_brain.errors import VerificationError


def _leftovers(directory: Path) -> list[Path]:
    return sorted(directory.rglob(".tmp-*"))


def test_atomic_write_creates_file_and_refuses_second_write(tmp_path: Path):
    path = tmp_path / "v1.json"
    atomic_write(path, b'{"version": 1}\n')
    assert path.read_bytes() == b'{"version": 1}\n'
    with pytest.raises(VerificationError, match="refusing to overwrite"):
        atomic_write(path, b'{"version": 2}\n')
    assert path.read_bytes() == b'{"version": 1}\n'
    assert _leftovers(tmp_path) == []


def test_atomic_write_refuses_preexisting_destination(tmp_path: Path):
    path = tmp_path / "v1.json"
    path.write_bytes(b"ORIGINAL")
    with pytest.raises(VerificationError, match="refusing to overwrite"):
        atomic_write(path, b"NEW")
    assert path.read_bytes() == b"ORIGINAL"
    assert _leftovers(tmp_path) == []


def test_atomic_write_race_planted_destination_survives(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Destination created immediately before publication must survive.

    The planted destination is injected at a point shared by both
    implementations: immediately after the temporary file's file-sync
    completes, before publication. Old implementation: os.replace
    overwrites the planted bytes and this test fails on the bytes
    assertion. Patched implementation: os.link raises FileExistsError,
    mapped to VerificationError, and the planted bytes survive.
    Note: patching ella_brain._io.os.fsync patches the shared os
    module for the duration of this test; monkeypatch restores it
    afterwards.
    """
    path = tmp_path / "v1.json"
    real_fsync = os.fsync
    state = {"planted": False}

    def planting_fsync(fd, *args, **kwargs):
        result = real_fsync(fd, *args, **kwargs)
        if not state["planted"]:
            state["planted"] = True
            path.write_bytes(b"PLANTED")
        return result

    monkeypatch.setattr("ella_brain._io.os.fsync", planting_fsync)
    raised = None
    try:
        atomic_write(path, b"NEW")
    except VerificationError as exc:
        raised = exc
    # Bytes first: on old code this is the assertion that fails,
    # proving the overwrite rather than only a missing exception.
    assert path.read_bytes() == b"PLANTED", "planted destination was overwritten"
    assert raised is not None
    assert "refusing to overwrite" in str(raised)
    assert _leftovers(tmp_path) == []


def test_atomic_write_non_collision_link_failure_propagates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """A non-collision os.link failure is not a collision: it propagates,
    the destination stays absent, and the temporary file is removed."""
    path = tmp_path / "v1.json"

    def failing_link(*args, **kwargs):
        raise PermissionError("simulated link failure")

    monkeypatch.setattr("ella_brain._io.os.link", failing_link)
    with pytest.raises(PermissionError, match="simulated link failure"):
        atomic_write(path, b"NEW")
    assert not path.exists()
    assert _leftovers(tmp_path) == []


def test_atomic_write_first_dir_sync_failure_keeps_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """First directory sync fails after linking: the error propagates,
    the complete destination survives, and the temporary name is
    removed. Per §2, the caller must reconcile disk state; the
    exception does not mean no write occurred."""

    def failing_first(*args, **kwargs):
        raise OSError("simulated first dir sync failure")

    monkeypatch.setattr("ella_brain._io._fsync_dir", failing_first)
    path = tmp_path / "v1.json"
    with pytest.raises(OSError, match="simulated first dir sync failure"):
        atomic_write(path, b"NEW")
    assert path.read_bytes() == b"NEW"
    assert _leftovers(tmp_path) == []


def test_atomic_write_second_dir_sync_failure_keeps_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Second directory sync fails: the error propagates and the
    destination survives (the temporary name was already removed
    before the second sync)."""
    calls: list[int] = []

    def failing_second(*args, **kwargs):
        calls.append(1)
        if len(calls) == 2:
            raise OSError("simulated second dir sync failure")

    monkeypatch.setattr("ella_brain._io._fsync_dir", failing_second)
    path = tmp_path / "v1.json"
    with pytest.raises(OSError, match="simulated second dir sync failure"):
        atomic_write(path, b"NEW")
    assert path.read_bytes() == b"NEW"
    assert _leftovers(tmp_path) == []


def test_atomic_write_dangling_symlink_is_not_replaced(tmp_path: Path):
    """A preexisting dangling destination symlink is not replaced.

    The pre-check uses path.exists(), which is False for a dangling
    symlink, so this exercises the link guard rather than the
    pre-check. Under old code, os.replace would have replaced the
    symlink itself and succeeded, so this test also fails on old
    code — for an overwrite reason, not a missing-exception reason."""
    target = tmp_path / "missing-target"
    path = tmp_path / "v1.json"
    path.symlink_to(target)
    assert path.is_symlink() and not path.exists()
    with pytest.raises(VerificationError, match="refusing to overwrite"):
        atomic_write(path, b"NEW")
    assert path.is_symlink()
    assert Path(os.readlink(path)) == target
    assert not target.exists()
    assert _leftovers(tmp_path) == []
