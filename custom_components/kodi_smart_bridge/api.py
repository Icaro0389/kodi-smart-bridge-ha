"""Authenticated access to the Kodi Smart Bridge. IPTV URLs stay in Kodi LXC."""
from __future__ import annotations

import asyncio
import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import CONF_TOKEN

class BridgeUnavailable(Exception):
    """Unavailable, denied or malformed response."""

class BridgeClient:
    def __init__(self, hass, host: str, port: int, token: str):
        self.url = f"http://{host}:{port}"
        self.token = token
        self.session = async_get_clientsession(hass)

    async def request(self, method: str, path: str, data: dict | None = None):
        if path not in ("/v1/health", "/v1/roots", "/v1/browse", "/v1/play"):
            raise BridgeUnavailable("Unsupported operation")
        try:
            async with self.session.request(
                method, self.url + path,
                json=data if method == "POST" else None,
                headers={"Authorization": "Bearer " + self.token},
                timeout=aiohttp.ClientTimeout(total=25),
                allow_redirects=False,
            ) as response:
                if response.status != 200:
                    # Do not forward the remote error response: it may contain credentials.
                    raise BridgeUnavailable(f"Bridge HTTP status {response.status}")
                body = await response.json(content_type=None)
                if not isinstance(body, dict):
                    raise BridgeUnavailable("Invalid bridge response")
                return body
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as exc:
            raise BridgeUnavailable("Bridge connection failed") from exc
