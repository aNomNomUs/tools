"""Minimal HTTP API using only the Python standard library."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

from .compatibility import compatibility_report
from .horoscope import HoroscopeEngine
from .profile import profile_payload
from .utils import sanitize_sign_name


@dataclass
class ApiResponse:
    status: int
    payload: Dict[str, Any]

    def to_bytes(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class AstroRequestHandler(BaseHTTPRequestHandler):
    server_version = "AstroTalkClone/1.0"

    def _send_response(self, response: ApiResponse) -> None:
        self.send_response(response.status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(response.to_bytes())

    def do_GET(self) -> None:  # noqa: N802 - stdlib signature
        try:
            if self.path.startswith("/healthz"):
                self._send_response(ApiResponse(HTTPStatus.OK, {"ok": True}))
                return
            if self.path.startswith("/horoscope"):
                response = self._handle_horoscope()
            elif self.path.startswith("/compatibility"):
                response = self._handle_compatibility()
            elif self.path.startswith("/profile"):
                response = self._handle_profile()
            else:
                response = ApiResponse(HTTPStatus.NOT_FOUND, {"error": "Endpoint not found."})
        except Exception as exc:  # pragma: no cover - defensive guard
            response = ApiResponse(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        self._send_response(response)

    def _handle_horoscope(self) -> ApiResponse:
        params = _parse_query(self.path)
        sign = sanitize_sign_name(params.get("sign", ""))
        day = _parse_date(params.get("date"))
        text = HoroscopeEngine().generate(sign, day)
        return ApiResponse(HTTPStatus.OK, {"sign": sign, "date": day.isoformat(), "horoscope": text})

    def _handle_compatibility(self) -> ApiResponse:
        params = _parse_query(self.path)
        primary = sanitize_sign_name(params.get("primary", ""))
        partner = sanitize_sign_name(params.get("partner", ""))
        report = compatibility_report(primary, partner)
        return ApiResponse(HTTPStatus.OK, report)

    def _handle_profile(self) -> ApiResponse:
        params = _parse_query(self.path)
        name = params.get("name", "").strip()
        birthday = _parse_date(params.get("birthday"))
        payload = profile_payload(name, birthday)
        return ApiResponse(HTTPStatus.OK, payload)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003 - stdlib override
        # Avoid noisy stdout in automated runs. Could be wired to logging if needed.
        pass


def _parse_query(path: str) -> Dict[str, str]:
    try:
        query_string = path.split("?", 1)[1]
    except IndexError:
        return {}
    params: Dict[str, str] = {}
    for pair in query_string.split("&"):
        if not pair:
            continue
        if "=" not in pair:
            raise ValueError("Malformed query parameter.")
        key, value = pair.split("=", 1)
        params[key] = value
    return params


def _parse_date(raw: str | None) -> date:
    if not raw:
        raise ValueError("Date query parameter is required.")
    parts = [int(part) for part in raw.split("-")]
    if len(parts) != 3:
        raise ValueError("Date must be YYYY-MM-DD.")
    return date(parts[0], parts[1], parts[2])


def serve(port: int = 8080) -> None:
    server = HTTPServer(("0.0.0.0", port), AstroRequestHandler)
    print(f"Serving AstroTalk clone on http://0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":  # pragma: no cover
    serve()
