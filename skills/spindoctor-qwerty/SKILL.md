---
name: spindoctor-qwerty
description: Show the complete SpinDoctor function table, run classical circuits and 241 presets, and test local file/text or confirmed chat theories with reports.
license: GPL-3.0-or-later
metadata:
  author: RUSSELL PHILIP SMITHSON
  version: "1.1.0"
---

# SpinDoctor Qwerty 1.1.0 for OpenHands

Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>.
Classical FP64 simulation on this computer; no quantum hardware or quantum advantage.

On first use, or a help/functions request, call `spindoctor_functions` and display its returned
Markdown table **verbatim**: Function | What it does | Command to type. `section="all"` also lists
all 241 presets. With one server the SDK exposes the six names below; multiple MCP servers may add
server prefixes. Use the names actually advertised by the host.

| Tool | Purpose |
| --- | --- |
| `spindoctor_functions` | Complete function table, gates and presets |
| `spindoctor_run_script` | Newline-separated q.* script, at most 200 commands |
| `spindoctor_run_preset` | `qc-001` through `qc-241`, string-valued overrides |
| `spindoctor_list_presets` | List or filter all presets |
| `spindoctor_report` | List/read workspace TXT reports |
| `spindoctor_test_theory` | Extract/test a local file, pasted text or confirmed chat theory |

For a chat theory, summarize claims, assumptions, variables and measurable prediction and obtain
the **user's confirmation** before testing. Submit that confirmed summary with `source="chat"`,
optional quoted `excerpts`, `hypothesis`, `prediction`, `script` and machine `checks`. Report
supported / not supported / inconclusive within simulator limits. The plugin cannot retrieve host
attachments or conversation history; supply a local file path or pasted text. Use `action="extract"`
when a theory needs interpretation first.

Use absolute local file and workspace paths. The MCP working directory is OpenHands' plugin data
directory; it is not the conversation workspace. Persistent reports default to
`~/spindoctor-workspace`. Choose another directory with the installation helper's `--workspace`,
an explicit `SPINDOCTOR_WORKSPACE` entry in `mcp.json`'s server environment, or a per-call `workspace`.
Setting a custom variable only in the parent shell may not reach the SDK's MCP child. Keep outputs outside the
installed plugin. The MCP server handles calls serially; separate processes should use separate
workspaces. Python is launched with `-B`, without a shell or installation hooks.

Limits: 298 logical qubits, at most 59 per entangled factor, dense storage `2^n × 16` bytes subject
to memory budget. Above 29 qubits prepared-factor sampling supports basis Z only; full joint analysis
is limited to 16 qubits. `mcx7` has seven controls and one target. Folder ingestion is synchronous:
128 top-level supported files, 4 MiB each, 128 commands per file and 4096 characters per command.
`q.folder cancel` has no background task to cancel; `q.compile synthesize` is unavailable.
Engine 1.1.0 implements SpinDoctor 3.1.2 build `3.1.2-298-20261010`.

If the tools are unavailable, show the host loading error and verify the MCP executable exists on
the host PATH. A local CLI alternative is the installed `engine/scripts/spindoctor_cli.py`, invoked
with Python and `-B` using its absolute path. Never invent results or claim a real quantum run.
