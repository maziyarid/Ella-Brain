"""Browser-channel adapter against a disposable store.

Requires ELLA_BRAIN_PIN_ROOT to be a checkout of
d01d1f15f0048d3a5874b59fb6c0759e508c6539. This file does not merge that branch.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path
from uuid import uuid5

import pytest

PIN = Path(os.environ.get("ELLA_BRAIN_PIN_ROOT", ""))
ROOT = Path(__file__).resolve().parents[1]
if not PIN.is_dir():
    raise RuntimeError("Set ELLA_BRAIN_PIN_ROOT to the hardening checkout. Do not merge it.")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PIN))

from ella_channel.server import serve  # noqa: E402
from ella_channel.synthetic import NS  # noqa: E402


def _post(port: int, path: str, body: dict, token: str = "") -> tuple[int, dict]:
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def _get(port: int, path: str, token: str, session_id: str) -> tuple[int, dict]:
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        headers={"Authorization": f"Bearer {token}", "X-Ella-Session": session_id},
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def _start(tmp_path: Path, hold: threading.Event | None = None):
    httpd = serve(tmp_path, "127.0.0.1", 0, hold)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def _versions(root: Path, kind: str, entity_id: str) -> list[Path]:
    directory = root / kind / entity_id
    if not directory.is_dir():
        return []
    return sorted(directory.glob("v*.json"))


def test_guest_cannot_mutate_even_if_the_reviewer_flag_is_set(tmp_path: Path) -> None:
    httpd = _start(tmp_path)
    port = httpd.server_address[1]
    status, session = _post(
        port,
        "/v1/sessions",
        {"access": "guest", "principal": "local_reviewer"},
    )
    assert status == 200
    assert session["principal_ignored"] is True
    status, body = _post(
        port,
        "/v1/ops",
        {
            "session_id": session["session_id"],
            "request_id": "req-guest",
            "text": "کار مصنوعی را ثبت کن",
            "principal": "local_reviewer",
        },
        session["token"],
    )
    assert status == 403
    assert body["error"] == "guest_denied"
    assert _versions(tmp_path, "tasks", str(uuid5(NS, "req-guest:task"))) == []
    httpd.shutdown()


def test_roundtrip_readback_duplicate_and_invalid_dependency(tmp_path: Path) -> None:
    httpd = _start(tmp_path)
    port = httpd.server_address[1]
    _, session = _post(port, "/v1/sessions", {"access": "operator", "principal": "guest"})
    status, body = _post(
        port,
        "/v1/ops",
        {"session_id": session["session_id"], "request_id": "req-ok", "text": "کار مصنوعی را ثبت کن"},
        session["token"],
    )
    assert status == 200
    assert body["duplicate"] is False
    assert body["version"] == 1
    assert body["status"] == "pending"
    assert "حافظهٔ گفتگو نیست" in body["read_back"]
    task_id = body["id"]
    assert len(_versions(tmp_path, "tasks", task_id)) == 1

    status, again = _post(
        port,
        "/v1/ops",
        {"session_id": session["session_id"], "request_id": "req-ok", "text": "کار مصنوعی را ثبت کن"},
        session["token"],
    )
    assert status == 200
    assert again["duplicate"] is True
    assert again["version"] == 1
    assert len(_versions(tmp_path, "tasks", task_id)) == 1

    status, read = _get(port, f"/v1/entities/task/{task_id}", session["token"], session["session_id"])
    assert status == 200
    assert read["version"] == 1

    status, rejected = _post(
        port,
        "/v1/ops",
        {
            "session_id": session["session_id"],
            "request_id": "req-bad",
            "text": "وابستگی نامعتبر را امتحان کن",
        },
        session["token"],
    )
    assert status == 200
    assert rejected["ok"] is False
    assert rejected["version"] is None
    assert rejected["dep_version"] == 1
    assert _versions(tmp_path, "tasks", rejected["id"]) == []
    httpd.shutdown()


def test_cancel_before_mutate_writes_nothing(tmp_path: Path) -> None:
    hold = threading.Event()
    httpd = _start(tmp_path, hold)
    port = httpd.server_address[1]
    _, session = _post(port, "/v1/sessions", {"access": "operator"})
    box: dict = {}

    def call() -> None:
        box["result"] = _post(
            port,
            "/v1/ops",
            {"session_id": session["session_id"], "request_id": "req-cancel", "text": "کار مصنوعی را ثبت کن"},
            session["token"],
        )

    worker = threading.Thread(target=call)
    worker.start()
    assert httpd.channel.hold_entered.wait(timeout=2)
    status, _ = _post(
        port,
        "/v1/cancel",
        {"session_id": session["session_id"], "request_id": "req-cancel"},
        session["token"],
    )
    assert status == 200
    hold.set()
    worker.join(timeout=3)
    assert box["result"][0] == 409
    assert _versions(tmp_path, "tasks", str(uuid5(NS, "req-cancel:task"))) == []
    httpd.shutdown()


def test_restart_keeps_the_store_and_drops_authority(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PIN}{os.pathsep}{ROOT}"
    port = 18771

    def spawn() -> subprocess.Popen[str]:
        return subprocess.Popen(
            [sys.executable, "-m", "ella_channel.server", "--store", str(tmp_path), "--port", str(port)],
            cwd="/tmp",
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    first = spawn()
    assert first.stdout is not None
    line = first.stdout.readline()
    assert "listening" in line
    _, session = _post(port, "/v1/sessions", {"access": "operator"})
    status, created = _post(
        port,
        "/v1/ops",
        {"session_id": session["session_id"], "request_id": "req-live", "text": "کار مصنوعی را ثبت کن"},
        session["token"],
    )
    assert status == 200
    task_id = created["id"]
    first.terminate()
    first.wait(timeout=5)

    second = spawn()
    assert second.stdout is not None
    assert "listening" in second.stdout.readline()
    status, denied = _post(
        port,
        "/v1/ops",
        {"session_id": session["session_id"], "request_id": "req-live", "text": "کار مصنوعی را ثبت کن"},
        session["token"],
    )
    assert status == 401
    _, fresh = _post(port, "/v1/sessions", {"access": "operator"})
    status, read = _get(port, f"/v1/entities/task/{task_id}", fresh["token"], fresh["session_id"])
    assert status == 200
    assert read["version"] == 1
    assert len(_versions(tmp_path, "tasks", task_id)) == 1
    second.terminate()
    second.wait(timeout=5)


def test_unpinned_ella_brain_is_refused(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    proc = subprocess.run(
        [sys.executable, "-m", "ella_channel.server", "--store", str(tmp_path), "--port", "18772"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode != 0
    assert "pin mismatch" in proc.stderr + proc.stdout
