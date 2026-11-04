"""Localhost adapter from the browser session to Ella.get and Ella.mutate.

Authority lives in this process. A restart keeps the version files and drops
every token. The browser reviewer flag is ignored.
"""

from __future__ import annotations

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

from ella_channel.pin import BASELINE_SHA, verify_imported_gate
from ella_channel.synthetic import invalid_dependency, roundtrip
from ella_brain import Ella

PHRASES = json.loads((Path(__file__).with_name("phrases.json")).read_text(encoding="utf-8"))
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _host_of(value: str) -> str:
    return (urlsplit(f"//{value}").hostname or "").lower()


def is_local_request(client_ip: str, headers: Any) -> bool:
    """True only for a loopback client with no sign of a non-local hop.

    Any forwarding header refuses. Host and Origin must name loopback, so a
    same-machine proxy reached from another host (Host 192.168.x.y) refuses.
    This is a prototype boundary, not authentication: any local process passes.
    """
    if client_ip not in ("127.0.0.1", "::1"):
        return False
    for name in ("X-Forwarded-For", "X-Forwarded-Host", "X-Real-IP", "Forwarded"):
        if headers.get(name):
            return False
    if _host_of(headers.get("Host") or "") not in LOOPBACK_HOSTS:
        return False
    origin = headers.get("Origin")
    if origin and (urlsplit(origin).hostname or "").lower() not in LOOPBACK_HOSTS:
        return False
    return True


OPS = {
    PHRASES["roundtrip"]: "roundtrip",
    PHRASES["invalid_dependency"]: "invalid_dependency",
}


class Channel:
    def __init__(self, root: Path, hold: threading.Event | None = None) -> None:
        self.gate_files = verify_imported_gate()
        self.root = root
        self.ella = Ella(root)
        self.lock = threading.Lock()
        self.hold = hold
        self.hold_entered = threading.Event()
        self.sessions: dict[str, dict[str, str]] = {}
        self.cancelled: set[str] = set()
        self.receipts: dict[str, dict[str, Any]] = {}

    def open_session(self, body: dict[str, Any], local: bool = True) -> dict[str, Any]:
        access = body.get("access")
        if access not in ("guest", "operator"):
            raise ValueError("access must be guest or operator")
        if access == "operator" and not local:
            raise LookupError("operator sessions are granted only to local, unproxied requests")
        token = uuid4().hex
        session_id = str(uuid4())
        with self.lock:
            self.sessions[token] = {"session_id": session_id, "access": access}
        return {
            "session_id": session_id,
            "token": token,
            "access": access,
            "principal_ignored": True,
            "baseline": BASELINE_SHA,
            "gate_files": self.gate_files,
        }

    def cancel(self, token: str, body: dict[str, Any]) -> dict[str, Any]:
        session = self._session(token, body.get("session_id"))
        request_id = str(body.get("request_id") or "")
        if not request_id:
            raise ValueError("request_id is required")
        with self.lock:
            self.cancelled.add(self._key(session["session_id"], request_id))
        return {"ok": True, "cancelled": request_id}

    def operate(self, token: str, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        session = self._session(token, body.get("session_id"))
        if session["access"] != "operator":
            return 403, {
                "ok": False,
                "error": "guest_denied",
                "read_back": "مهمان اجازهٔ این کار را ندارد. هیچ نسخه‌ای نوشته نشد.",
            }
        request_id = str(body.get("request_id") or "")
        text = " ".join(str(body.get("text") or "").split())
        op_name = OPS.get(text)
        if not request_id or op_name is None:
            return 422, {"ok": False, "error": "not_a_gate_utterance", "read_back": "این جمله به درگاه نمی‌رود."}
        key = self._key(session["session_id"], request_id)
        with self.lock:
            if key in self.cancelled:
                return 409, {"ok": False, "error": "cancelled", "read_back": "درخواست لغو شده اجرا نشد."}
            cached = self.receipts.get(key)
            if cached is not None:
                return 200, {**cached, "duplicate": True}
        if self.hold is not None:
            self.hold_entered.set()
            self.hold.wait(timeout=2)
        with self.lock:
            if key in self.cancelled:
                return 409, {"ok": False, "error": "cancelled", "read_back": "درخواست لغو شده اجرا نشد."}
            cached = self.receipts.get(key)
            if cached is not None:
                return 200, {**cached, "duplicate": True}
            if op_name == "roundtrip":
                receipt = roundtrip(self.ella, request_id)
            else:
                receipt = invalid_dependency(self.ella, request_id)
            receipt = {**receipt, "duplicate": False, "request_id": request_id}
            self.receipts[key] = receipt
            return 200, receipt

    def read(self, token: str, session_id: str, entity_id: str) -> tuple[int, dict[str, Any]]:
        session = self._session(token, session_id)
        if session["access"] != "operator":
            return 403, {"ok": False, "error": "guest_denied"}
        doc = self.ella.get("task", entity_id)
        return 200, {
            "ok": True,
            "id": str(doc.id),
            "type": doc.type.value,
            "status": doc.status.value,
            "version": doc.version,
        }

    def _session(self, token: str, session_id: Any) -> dict[str, str]:
        with self.lock:
            found = self.sessions.get(token)
        if found is None or found["session_id"] != session_id:
            raise PermissionError("session token is not valid")
        return found

    @staticmethod
    def _key(session_id: str, request_id: str) -> str:
        return f"{session_id}:{request_id}"


def make_handler(channel: Channel) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            return

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length") or "0")
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                self._send(400, {"ok": False, "error": "bad_json"})
                return
            token = _bearer(self.headers.get("Authorization"))
            try:
                if self.path == "/v1/sessions":
                    local = is_local_request(self.client_address[0], self.headers)
                    self._send(200, channel.open_session(body, local))
                    return
                if self.path == "/v1/cancel":
                    self._send(200, channel.cancel(token, body))
                    return
                if self.path == "/v1/ops":
                    status, payload = channel.operate(token, body)
                    self._send(status, payload)
                    return
            except PermissionError as exc:
                self._send(401, {"ok": False, "error": "unauthorized", "read_back": str(exc)})
                return
            except LookupError as exc:
                self._send(403, {"ok": False, "error": "operator_not_local", "read_back": str(exc)})
                return
            except ValueError as exc:
                self._send(400, {"ok": False, "error": "bad_request", "read_back": str(exc)})
                return
            self._send(404, {"ok": False, "error": "not_found"})

        def do_GET(self) -> None:  # noqa: N802
            if not self.path.startswith("/v1/entities/task/"):
                self._send(404, {"ok": False, "error": "not_found"})
                return
            entity_id = self.path.removeprefix("/v1/entities/task/").split("?")[0]
            session_id = self.headers.get("X-Ella-Session") or ""
            token = _bearer(self.headers.get("Authorization"))
            try:
                status, payload = channel.read(token, session_id, entity_id)
            except PermissionError as exc:
                self._send(401, {"ok": False, "error": "unauthorized", "read_back": str(exc)})
                return
            self._send(status, payload)

        def _send(self, status: int, payload: dict[str, Any]) -> None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return Handler


def _bearer(header: str | None) -> str:
    if not header or not header.startswith("Bearer "):
        return ""
    return header.removeprefix("Bearer ").strip()


def serve(root: Path, host: str, port: int, hold: threading.Event | None = None) -> ThreadingHTTPServer:
    channel = Channel(root, hold)
    httpd = ThreadingHTTPServer((host, port), make_handler(channel))
    httpd.channel = channel  # type: ignore[attr-defined]
    return httpd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    root = Path(args.store)
    root.mkdir(parents=True, exist_ok=True)
    httpd = serve(root, args.host, args.port)
    print(f"listening {args.host}:{httpd.server_address[1]} baseline {BASELINE_SHA}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
