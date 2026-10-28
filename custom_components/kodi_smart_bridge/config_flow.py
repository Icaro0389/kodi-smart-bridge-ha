"""UI-based setup. No YAML and no token in Lovelace."""
from __future__ import annotations

import ipaddress
import probatio as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from .api import BridgeClient, BridgeUnavailable
from .const import DOMAIN, CONF_TOKEN, DEFAULT_HOST, DEFAULT_PORT

class KodiSmartBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            try:
                # IP literals only, deliberately no arbitrary hostnames/URLs.
                host = str(ipaddress.IPv4Address(user_input[CONF_HOST]))
                port = user_input[CONF_PORT]
                if not 1 <= port <= 65535: raise ValueError()
                client = BridgeClient(self.hass, host, port, user_input[CONF_TOKEN])
                await client.request("GET", "/v1/health")
            except (ValueError, BridgeUnavailable):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=f"Kodi Smart Bridge ({host})", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(vol.Coerce(int), vol.Range(min=1,max=65535)),
                vol.Required(CONF_TOKEN): str,
            }),
            errors=errors,
        )


    async def async_step_reconfigure(self, user_input=None):
        """Reconfigure the existing bridge without replacing its entry."""
        entry = self._get_reconfigure_entry()
        errors = {}

        if user_input is not None:
            try:
                host = str(
                    ipaddress.IPv4Address(user_input[CONF_HOST])
                )
                port = int(user_input[CONF_PORT])
                if not 1 <= port <= 65535:
                    raise ValueError()

                token = user_input[CONF_TOKEN]
                client = BridgeClient(
                    self.hass, host, port, token
                )
                await client.request("GET", "/v1/health")

            except (ValueError, BridgeUnavailable):
                errors["base"] = "cannot_connect"
            else:
                new_unique_id = f"{host}:{port}"

                duplicate = any(
                    other.entry_id != entry.entry_id
                    and other.unique_id == new_unique_id
                    for other in self.hass.config_entries.async_entries(
                        DOMAIN
                    )
                )

                if duplicate:
                    errors["base"] = "already_configured"
                else:
                    return self.async_update_reload_and_abort(
                        entry,
                        unique_id=new_unique_id,
                        title=f"Kodi Smart Bridge ({host})",
                        data_updates={
                            CONF_HOST: host,
                            CONF_PORT: port,
                            CONF_TOKEN: token,
                        },
                    )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_HOST,
                    default=entry.data[CONF_HOST]
                ): str,
                vol.Required(
                    CONF_PORT,
                    default=entry.data[CONF_PORT]
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1, max=65535)
                ),
                vol.Required(CONF_TOKEN): str,
            }),
            errors=errors,
        )

