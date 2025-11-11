"""
Lightweight Home Assistant WebSocket client used by the E2E tests.

The official HA WebSocket API is documented at:
https://developers.home-assistant.io/docs/api/websocket/#websocket-api
This helper implements just enough of the protocol for the Phase 3
integration tests (state queries, service calls, registry access).
"""

from __future__ import annotations

import asyncio
import contextlib
import json
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urlunparse

import aiohttp


class HomeAssistantClient:
    """Minimal async client for the Home Assistant WebSocket API."""

    def __init__(self, url: str, token: str, *, request_timeout: float = 10.0) -> None:
        self._url = url
        self._token = token
        self._request_timeout = request_timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._listener_task: Optional[asyncio.Task] = None
        self._pending: Dict[int, asyncio.Future] = {}
        self._msg_id = 0
        self._id_lock = asyncio.Lock()

    async def connect(self) -> None:
        """Open WebSocket connection and authenticate."""
        if self._ws is not None:
            return

        self._session = aiohttp.ClientSession()
        websocket_url = self._normalize_url(self._url)
        self._ws = await self._session.ws_connect(websocket_url, heartbeat=30)

        # Expect auth challenge from HA
        auth_required = await self._ws.receive_json()
        if auth_required.get("type") != "auth_required":
            raise RuntimeError("Unexpected handshake response from Home Assistant")

        await self._ws.send_json({"type": "auth", "access_token": self._token})
        auth_result = await self._ws.receive_json()
        if auth_result.get("type") != "auth_ok":
            raise RuntimeError(f"Authentication failed: {auth_result}")

        self._listener_task = asyncio.create_task(self._listen())

    async def disconnect(self) -> None:
        """Close the WebSocket connection."""
        current_task = asyncio.current_task()
        if self._listener_task and self._listener_task is not current_task:
            self._listener_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._listener_task
        self._listener_task = None

        if self._ws:
            await self._ws.close()
            self._ws = None

        if self._session:
            await self._session.close()
            self._session = None

        # Fail any pending requests
        while self._pending:
            _, fut = self._pending.popitem()
            if not fut.done():
                fut.set_exception(RuntimeError("Connection closed"))

    async def _send_command(
        self,
        payload: Dict[str, Any],
        *,
        timeout: Optional[float] = None,
    ) -> Any:
        """Send a command and wait for the matching response."""
        if not self._ws:
            raise RuntimeError("Client is not connected")

        async with self._id_lock:
            self._msg_id += 1
            msg_id = self._msg_id

        fut: asyncio.Future = asyncio.get_running_loop().create_future()
        self._pending[msg_id] = fut

        message = dict(payload)
        message["id"] = msg_id
        await self._ws.send_json(message)

        return await asyncio.wait_for(
            fut,
            timeout=timeout or self._request_timeout,
        )

    async def _listen(self) -> None:
        """Background listener that routes responses back to awaiting callers."""
        assert self._ws is not None

        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    msg_id = data.get("id")
                    if msg_id is not None and msg_id in self._pending:
                        fut = self._pending.pop(msg_id)
                        if data.get("type") == "result" and data.get("success", True):
                            fut.set_result(data.get("result"))
                        else:
                            fut.set_exception(
                                RuntimeError(f"Request {msg_id} failed: {data}")
                            )
                elif msg.type in (
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.ERROR,
                ):
                    break
        except asyncio.CancelledError:
            raise
        finally:
            # Ensure connection teardown if listener stops unexpectedly
            await self.disconnect()

    async def get_devices(self) -> List[Dict[str, Any]]:
        """Return the full device registry."""
        result = await self._send_command({"type": "config/device_registry/list"})
        return result or []

    async def get_services(self) -> Dict[str, Any]:
        """Return available services keyed by domain."""
        result = await self._send_command({"type": "get_services"})
        return result or {}

    async def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Fetch the state dictionary for the given entity."""
        states = await self._send_command({"type": "get_states"})
        return next(
            (s for s in (states or []) if s["entity_id"] == entity_id),
            None,
        )

    async def call_service(
        self,
        domain: str,
        service: str,
        **service_data: Any,
    ) -> Any:
        """Call a Home Assistant service and return the result payload."""
        payload = {
            "type": "call_service",
            "domain": domain,
            "service": service,
            "service_data": service_data,
        }
        return await self._send_command(payload)

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Convert http(s) URLs into ws(s) endpoints if needed."""
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()

        if scheme in {"ws", "wss"}:
            path = parsed.path or "/api/websocket"
            if not path.endswith("/api/websocket"):
                path = path.rstrip("/") + "/api/websocket"
            return urlunparse(parsed._replace(path=path))

        if scheme not in {"http", "https"}:
            raise ValueError(f"Unsupported HA_URL scheme: {scheme}")

        ws_scheme = "wss" if scheme == "https" else "ws"
        path = parsed.path or ""
        if not path.endswith("/api/websocket"):
            path = path.rstrip("/") + "/api/websocket"

        return urlunparse(
            (
                ws_scheme,
                parsed.netloc,
                path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )
