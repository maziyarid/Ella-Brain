"""Browser-channel adapter against a disposable store.

Uses this repository's ella_brain. The server refuses to start unless the
imported _io.py and _stages.py match main
9132753e4be980c75269be6de2658134e4960208.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path
from uuid import uuid5

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ella_channel.pin import PIN_IO_SHA256, PIN_STAGES_SHA256, verify_imported_gate  # noqa: E402
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


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _child_env() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("ELLA_BRAIN_PIN_ROOT", None)
    env.pop("PYTHONPATH", None)
    return env


def test_restart_keeps_the_store_and_drops_authority(tmp_path: Path) -> None:
    env = _child_env()
    port = _free_port()

    def spawn() -> subprocess.Popen[str]:
        return subprocess.Popen(
            [sys.executable, "-m", "ella_channel.server", "--store", str(tmp_path), "--port", str(port)],
            cwd=ROOT,
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


def test_imported_gate_is_this_checkout() -> None:
    import ella_brain._io as io_module
    import ella_brain._stages as stages_module

    io_path = Path(io_module.__file__).resolve()
    stages_path = Path(stages_module.__file__).resolve()
    assert io_path.is_relative_to(ROOT)
    assert stages_path.is_relative_to(ROOT)
    found = verify_imported_gate()
    assert found["ella_brain/_io.py"] == PIN_IO_SHA256
    assert found["ella_brain/_stages.py"] == PIN_STAGES_SHA256


def test_tampered_gate_file_is_refused(tmp_path: Path) -> None:
    for name in ("_io.py", "_stages.py"):
        pkg_parent = tmp_path / name
        shutil.copytree(ROOT / "ella_brain", pkg_parent / "ella_brain")
        target = pkg_parent / "ella_brain" / name
        target.write_bytes(target.read_bytes() + b"\n# tampered\n")
        env = _child_env()
        env["PYTHONPATH"] = f"{pkg_parent}{os.pathsep}{ROOT}"
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "ella_channel.server",
                "--store",
                str(tmp_path / f"store-{name}"),
                "--port",
                "0",
            ],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert proc.returncode != 0
        combined = proc.stderr + proc.stdout
        assert "pin mismatch" in combined
        assert name in combined



def _post_headers(port: int, path: str, body: dict, headers: dict) -> tuple[int, dict]:
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_operator_session_requires_a_local_unproxied_request(tmp_path: Path) -> None:
    httpd = _start(tmp_path)
    port = httpd.server_address[1]
    try:
        status, local = _post_headers(port, "/v1/sessions", {"access": "operator"}, {})
        assert status == 200 and local["access"] == "operator"
        remote_shapes = [
            {"Host": "192.168.1.20:5173"},
            {"X-Forwarded-For": "10.0.0.7"},
            {"Forwarded": "for=10.0.0.7"},
            {"Origin": "http://192.168.1.20:5173"},
        ]
        for headers in remote_shapes:
            status, denied = _post_headers(port, "/v1/sessions", {"access": "operator"}, headers)
            assert status == 403, headers
            assert denied["error"] == "operator_not_local"
            assert "token" not in denied
            status, guest = _post_headers(port, "/v1/sessions", {"access": "guest"}, headers)
            assert status == 200 and guest["access"] == "guest", headers
    finally:
        httpd.shutdown()
