"""Kodi Smart Bridge: private WebSocket gateway for Lovelace."""
from __future__ import annotations

import probatio as vol
from homeassistant import config_entries
from homeassistant.components import websocket_api
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .api import BridgeClient, BridgeUnavailable
from .const import CONF_TOKEN, DOMAIN

ROOTS = ("film", "series", "movies", "tv", "radio")

def get_bridge(hass):
    clients = hass.data.get(DOMAIN, {})
    if not clients:
        raise BridgeUnavailable("Kodi Smart Bridge not configured")
    return next(iter(clients.values()))

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    websocket_api.async_register_command(hass, ws_roots)
    websocket_api.async_register_command(hass, ws_browse)
    websocket_api.async_register_command(hass, ws_play)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = BridgeClient(
        hass, entry.data[CONF_HOST], entry.data[CONF_PORT], entry.data[CONF_TOKEN]
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True

@websocket_api.websocket_command({vol.Required("type"): "kodi_smart_bridge/roots"})
@websocket_api.async_response
async def ws_roots(hass, connection, msg):
    try:
        result = await get_bridge(hass).request("GET", "/v1/roots")
        connection.send_result(msg["id"], result)
    except BridgeUnavailable as exc:
        connection.send_error(msg["id"], "bridge_error", str(exc))

@websocket_api.websocket_command({
    vol.Required("type"): "kodi_smart_bridge/browse",
    vol.Optional("root"): vol.In(ROOTS),
    vol.Optional("item_id"): vol.All(str, vol.Length(min=1, max=128)),
    vol.Optional("group"): vol.All(str, vol.Length(max=100)),
    vol.Optional("search"): vol.All(str, vol.Length(max=100)),
    vol.Optional("page", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=10000)),
    vol.Optional("page_size", default=24): vol.All(vol.Coerce(int), vol.Range(min=1,max=100)),
})
@websocket_api.async_response
async def ws_browse(hass, connection, msg):
    if "root" not in msg and "item_id" not in msg:
        connection.send_error(msg["id"], "invalid_format", "root or item_id required")
        return
    data = {k: msg[k] for k in ("root", "group", "search", "page", "page_size") if k in msg}
    if "item_id" in msg:
        data["id"] = msg["item_id"]
    try:
        result = await get_bridge(hass).request("POST", "/v1/browse", data)
        connection.send_result(msg["id"], result)
    except BridgeUnavailable as exc:
        connection.send_error(msg["id"], "bridge_error", str(exc))

@websocket_api.websocket_command({
    vol.Required("type"): "kodi_smart_bridge/play",
    vol.Required("item_id"): vol.All(str, vol.Length(min=1, max=128)),
})
@websocket_api.async_response
async def ws_play(hass, connection, msg):
    # Playback is a privileged action. Root browsing works for signed-in users.
    if not connection.user.is_admin:
        connection.send_error(msg["id"], "unauthorized", "Administrator required")
        return
    try:
        result = await get_bridge(hass).request("POST", "/v1/play", {"id":msg["item_id"]})
        connection.send_result(msg["id"], result)
    except BridgeUnavailable as exc:
        connection.send_error(msg["id"], "bridge_error", str(exc))
