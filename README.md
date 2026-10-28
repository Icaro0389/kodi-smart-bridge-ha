# Kodi Smart Bridge — Home Assistant integration

Custom integration for connecting a Home Assistant dashboard card to a separately running Kodi Smart Bridge API. **Integration v0.1.2.**

## Prerequisites

- Running Kodi Smart Bridge server reachable by Home Assistant (e.g. the Home Assistant app on port `8790`).
- API bearer token configured in that server.
- The Kodi Smart Remote Lovelace card is a **separate** component/repository.

## Install with HACS

After publishing this directory as repository `Icaro0389/kodi-smart-bridge-ha`, add it to HACS as a **custom integration** repository. Install and restart Home Assistant Core. Then open **Settings → Devices & services → Add integration → Kodi Smart Bridge** and enter host, port and token.

**Private GitHub repositories may not be installable directly by HACS.** Keep the repository private during review and use the manual installation method below until ready for publication.

## Manual installation

Copy `custom_components/kodi_smart_bridge/` into `<HA config>/custom_components/kodi_smart_bridge/`. Restart Home Assistant Core and configure the integration from the GUI.

## Reconfigure without losing the entry

In **Settings → Devices & services → Kodi Smart Bridge**, choose **Reconfigure** for the existing entry. Provide the new IPv4 address, port and bearer token. The `/v1/health` endpoint is checked before changes are saved. The same config entry is updated and reloaded, preserving its entry ID.

## Security

- Never commit the bridge token, IPTV provider credentials or media playlists.
- The remote API uses HTTP on your local network; restrict it to trusted network peers or place it behind an authenticated secure proxy when appropriate.
- Playback WebSocket requests are restricted to Home Assistant administrators by the integration.

## Versioning

Initial GitHub packaging of the previously tested Home Assistant integration `v0.1.2`. Compared with the exported installation, only the default endpoint, user-facing strings and documentation have been adjusted. Runtime request and playback logic is unchanged.

## Rollback

Back up your installed `custom_components/kodi_smart_bridge` directory first. To restore a previous release, replace that directory with the backup and restart Home Assistant Core. Reconfigure the endpoint from the GUI if necessary.
