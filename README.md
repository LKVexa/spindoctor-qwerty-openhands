# SpinDoctor Qwerty for OpenHands

**1.1.0** packages SpinDoctor **3.1.2**, build `3.1.2-298-20261010`, as an Agent Plugins 1.0
plugin for OpenHands. The genuine OpenHands SDK **1.54.0** loader, MCP tools and Conversation
dispatcher were tested on Windows. See [E2E_RESULTS.md](E2E_RESULTS.md) for evidence and limits.

Copyright (C) 2026 **RUSSELL PHILIP SMITHSON** <russellsmithson77@outlook.com>.
Licensed under **GNU GPL version 3 or later**, SPDX `GPL-3.0-or-later`.
The complete GPL version 3 text is in [LICENSE](LICENSE); also see [NOTICE](NOTICE) and [COPYRIGHT](COPYRIGHT).

This is classical FP64 simulation on an ordinary computer. It does not connect to quantum hardware
and claims no quantum speed-up or quantum advantage. The bundled standard-library engine is
unchanged from the approved engine 1.1.0. OpenHands and other third-party runtimes are not bundled.

## Tools and behavior

| Tool | Purpose |
| --- | --- |
| `spindoctor_functions` | Return the complete Markdown function table, gates and presets |
| `spindoctor_run_script` | Run a newline-separated q.* script, at most 200 commands |
| `spindoctor_run_preset` | Run `qc-001` through `qc-241`, with string-valued overrides |
| `spindoctor_list_presets` | List or filter all 241 presets |
| `spindoctor_report` | List or read workspace TXT reports |
| `spindoctor_test_theory` | Extract or test a local file, pasted text or confirmed chat theory |

The first-use skill asks the assistant to display the function table verbatim. For a chat theory,
the assistant must summarize claims, assumptions, variables and a measurable prediction and obtain
the user's confirmation before running the test. Reports classify the result as supported, not
supported or inconclusive within simulator limits. These instructions guide the assistant; no real
model's compliance was tested. Supply local files or confirmed text: this plugin cannot fetch host
attachments or conversation history. [FUNCTIONS.md](FUNCTIONS.md) contains the command reference.

With one MCP server the SDK exposes the six names above. Multiple servers can add prefixes; use the
actual names advertised by the host. OpenHands preserves the engine's text and error status in its
MCP observation but discards MCP `structuredContent`. The function table remains Markdown; other
tool results are JSON text after the SDK's tool-execution header.

## Install in a new directory

The engine needs **Python 3.8 or later**; the tested OpenHands SDK needs **Python 3.12 or later**
and its own installed dependencies. Put the selected interpreter's directory on the host PATH.
Agent Plugins 1.0 requires a bare executable command, so an absolute Python executable cannot go
in `mcp.json.command`.

Clone this repository, then use the helper to create a separate, new installation. Choose a report
directory outside the installation and use absolute paths. In the commands below, replace the
angle-bracket values with your chosen paths:

```sh
git clone https://github.com/LKVexa/spindoctor-qwerty-openhands.git
cd spindoctor-qwerty-openhands
python -B tools/install_openhands.py --target "<absolute-new-plugin-directory>" --workspace "<absolute-report-directory>" --python-command python
```

On systems whose executable is `python3`, use `--python-command python3`. A Windows launcher can be
configured as `--python-command py --python-arg=-3`; the command and argument are stored separately.
The helper's launcher configuration was tested, but actually invoking `py -3` was not tested.
Existing destinations, including empty directories, are rejected without replacing their files.
The helper copies files and configures that copy; it does not register a global profile, install
dependencies or execute the simulator. Loading the release checkout directly is also supported by
the SDK, but keeping the configured copy separate makes its settings easier to manage.

Use the configured directory in an existing OpenHands SDK application:

```python
from pathlib import Path
from openhands.sdk import Conversation
from openhands.sdk.plugin import PluginSource

# agent is your configured OpenHands Agent with its own LLM.
with Conversation(
    agent,
    workspace=Path("<absolute-conversation-directory>"),
    plugins=[PluginSource(source="<absolute-new-plugin-directory>")],
) as conversation:
    conversation.send_message("Show the complete SpinDoctor function table.")
    conversation.run()
```

For loader inspection without a model, call `Plugin.load(<absolute-plugin-directory>)` from
`openhands.sdk`. The plugin contains root `plugin.json` and `mcp.json`,
`skills/spindoctor-qwerty/SKILL.md`, and OpenHands-specific command/agent/hook files under
`dev.openhands/`. This format follows the pinned SDK 1.54.0
[AgentPluginsFormat loader](https://github.com/OpenHands/software-agent-sdk/blob/1d471742ea7be017d013eaaa3080f5d28d5490cb/openhands-sdk/openhands/sdk/plugin/format/agent_plugins.py)
and the [Agent Plugins manifest](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json) and
[MCP configuration](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json) schemas.
The general [OpenHands plugin guide](https://docs.openhands.dev/sdk/guides/plugins) provides SDK usage
background but still shows the legacy layout; use this release's root manifests for SDK 1.54.0.

The SDK loads the confirmation skill, converts `qwerty-run` and `qwerty-preset` command files to
skills, and registers a self-contained `qwerty-helper` agent. Actual helper delegation and interactive
slash-command invocation remain untested. The hook file is empty; loading starts no simulator job.

## Paths, state and errors

Reports default to **`~/spindoctor-workspace`**, independently of the MCP working directory.
The helper's `--workspace` writes an explicit absolute `SPINDOCTOR_WORKSPACE` into the installed
MCP server's `env`. You can instead set that entry in the configured copy or pass an absolute
`workspace` with a tool call. A custom variable set only in the parent shell may not be forwarded:
the SDK's MCP transport inherits a fixed safe environment list. Do not assume it forwards arbitrary
workspace or seed variables. The reference tests explicitly configure their private server environment.

MCP `cwd` is `${PLUGIN_DATA}`, a host-managed data directory outside the installation. Relative
input paths resolve there, rather than in the Conversation workspace; use absolute local paths.
`${PLUGIN_ROOT}` and `${PLUGIN_DATA}` expand in MCP arguments, environment values and `cwd`.
They do not expand in `command`, and overriding these reserved environment names is invalid.
Python runs with `-B` and `PYTHONDONTWRITEBYTECODE=1`; engine state and reports stay outside the
plugin. Calls within one MCP process are serial; separate processes should use separate workspaces.

The SDK's tool executor defaults to a 300-second timeout. The direct native test harness sets the connected tool's
public executor timeout to 600 seconds and uses 60 seconds for discovery; Conversation tests keep SDK defaults. Agent Plugins 1.0 does not
allow a `timeout` field in this portable MCP server object. No vendor runtime checks were changed.
The loader rejects an invalid manifest; an invalid MCP document disables that component, and an
invalid individual server is skipped while valid siblings can remain. Unknown manifest fields may
be ignored with a warning, so loading alone is not proof that every setting was applied.

SDK 1.54.0 has a tested input-validation limitation: its generated action model does not enforce
the theory `source` enum or string-valued dictionary overrides. A `source="wrong"`, `action="extract"`
request with nonempty text was accepted and treated as text by the unchanged engine. A `shots=[]`
override for `qc-001` reached the engine and failed with an inapplicable-parameter error. That latter
result is not proof of general nested-type enforcement. The raw MCP schemas retain these constraints,
while the SDK's provider projection drops `additionalProperties`. Send the documented enum values
and string override values. These observed gaps are recorded as limitations, not successful strict
validation tests. Engine failures retain their JSON text and native error status.

## Simulator limits

The engine supports **298 logical qubits**, with at most **59** in one entangled factor. Dense state
storage needs `2^n × 16` bytes and is bounded by the memory budget; a 298-qubit result is not a dense
298-qubit statevector. Prepared-factor sampling above 29 qubits supports Z basis only, and full joint
analysis is limited to 16 qubits. `mcx7` uses seven controls and one target.

Folder ingestion is synchronous and limited to 128 top-level supported files, 4 MiB per file,
128 commands per file and 4096 characters per command. `q.folder cancel` has no background task to
cancel. `q.compile synthesize` is unavailable. File/text/chat theory tests and TXT/JSON/CSV/PDF
reports use the local engine; generated reports and host binaries are not shipped in this repository.

## Verification

The final native SDK characterization passed **49/49**, the genuine SDK Conversation suite passed
**14/14** with eight closed Conversations and 16 loopback provider requests, the fresh-copy helper
passed **18/18**, and the full native MCP and Conversation engine suites each passed **12/12**. These tests use the real SDK,
its loader, connected MCP tools and dispatcher. The model stand-in only chooses the requested tool
name/arguments and finishes after the result. It does not test model reasoning. Full results,
retained failed diagnostic runs, reproduction commands and uncompleted tests are in
[E2E_RESULTS.md](E2E_RESULTS.md).

Untested: a real model, the full OpenHands CLI/web interface or remote runtime, Linux/macOS,
another SDK version, interactive slash commands, helper-agent delegation and clean network SDK
bootstrap. The existing original source was preserved; [CHANGELOG.md](CHANGELOG.md) describes this release.
