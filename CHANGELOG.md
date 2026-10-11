# Changelog

## 1.1.0 — 2026-10-11

Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>.
GPL-3.0-or-later; see LICENSE, NOTICE and COPYRIGHT.

- Replaced the legacy hidden manifest/MCP layout with Agent Plugins 1.0 root `plugin.json` and
  `mcp.json`; moved OpenHands-specific commands, helper agent and empty hook file under `dev.openhands`.
- Bundled the unchanged approved engine 1.1.0 for SpinDoctor 3.1.2 build `3.1.2-298-20261010`:
  all six tools, 241 presets, 298 logical qubits and local file/text/confirmed-chat theory reports.
- Added the complete first-use function-table and chat-confirmation skill, full function reference,
  README, validation record and GPL version 3 or later author/copyright notices.
- Added a fresh-copy helper that preserves existing destinations, uses a bare PATH interpreter with
  separate arguments, configures an explicit external report workspace and disables Python caches.
- Kept MCP execution in host-managed plugin data, with default reports in `~/spindoctor-workspace`.
  Documented that arbitrary parent environment variables are not automatically forwarded to MCP.
- Made the helper agent's instructions self-contained after actual Conversation registration showed
  that its bundled-skill frontmatter reference was not resolved by the SDK's agent skill registry.
- Added genuine SDK loader/schema/action/observation checks, real Conversation tests with a loopback
  model-protocol stand-in, full engine E2E transports and preservation tests. Recorded SDK enum and
  nested dictionary validation gaps, provider-schema projection differences and all uncompleted tests.

The original 25-file integration remains preserved outside this release. No SDK/runtime guard or
approved engine file was modified. See E2E_RESULTS.md for the final results and retained failed runs.
