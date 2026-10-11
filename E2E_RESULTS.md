# OpenHands validation — 2026-10-11

Release **1.1.0**, SpinDoctor **3.1.2** build `3.1.2-298-20261010`, unchanged engine **1.1.0**.
Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>.
GPL-3.0-or-later; the complete GPL version 3 text is in LICENSE.

## Test boundary

Windows, genuine **OpenHands SDK 1.54.0**, Python **3.12.14**, FastMCP **3.4.8**, MCP **1.30.0**,
LiteLLM **1.105.0** and Pydantic **2.14.0**. Official SDK source pin:
`1d471742ea7be017d013eaaa3080f5d28d5490cb`. Five installed loader/MCP source syntax trees matched
that pin; the full runtime import preflight and dependency check passed. Host packages were
preinstalled outside the release. Clean network SDK bootstrap is not covered.

In the final configured tests, plugin copies, host persistence, logs, caches, temporary files and engine workspaces were isolated.
No existing profile, original source, approved engine, SDK code or runtime guard was altered.
No account, sign-in or real model was used. The genuine Conversation tests point their real SDK LLM
client at a loopback-only OpenAI-compatible protocol stand-in. It returns the requested tool name and
arguments, then calls the host's FinishTool after receiving the result. The real SDK performs plugin
loading, skill merge, agent registration, MCP connection, provider schema construction, native
ActionEvent execution and ObservationEvent handling. This covers integration, not model reasoning.

## Final checks

| Suite | Result | What was exercised |
| --- | --- | --- |
| Genuine SDK native characterization | **49/49** | Portable loader and offline native schemas, skill/command/agent/hook discovery, six connected tools, raw Markdown, 241 presets, scripts/state/report read, actual TXT/PDF existence, errors, confirmed chat, invalid manifests and nuanced MCP skip/disable behavior, cache-free execution and client closure; also explicit validation-gap observations below |
| Genuine SDK MCP engine E2E | **12/12**, 47.9 s | Complete engine suite below through actual SDK MCP tool/action/observation execution |
| Genuine SDK Conversation | **14/14** | Eight real Conversations, 16 loopback provider requests, actual merged confirmation/command skills and six advertised schemas, function/script/preset/report/theory dispatch, state across new Conversations, persisted reports, engine errors, native action/observation events and clean Conversation closure |
| Genuine SDK Conversation engine E2E | **12/12**, 73.1 s | Complete engine suite below, with every tool call dispatched by an actual Conversation through the loopback model protocol |
| Fresh-copy helper | **18/18** | Fresh paths with spaces, explicit workspace environment, bare Python with separate arguments, exact engine/license copy, GPL/full author metadata, skill/command/agent copy, existing/unrelated files preserved, invalid destinations/interpreters/placeholders/workspaces rejected, and separate `py -3` configuration |

The twelve engine checks cover protocol initialization, six-tool discovery, the raw function table,
241-preset listing, a script for every command family, a **298-qubit** circuit including `mcx7`, mixed
folder ingestion, theory tests from a local file, a confirmed chat summary with quoted excerpts and
an exported chat transcript, first-25 preset references and report validity. Presets `qc-001` through
`qc-025` matched **20 identically with five documented engine/reference differences**. Each complete
engine suite produced **255 structurally valid PDFs and 255 nonempty TXT twins**. PDF header, page,
xref, startxref and EOF checks passed. Optional `pdftotext` content inspection was unavailable;
visual PDF inspection was not performed.

The SDK MCP observation adds a tool-execution text header, preserves error status and engine text,
and discards MCP `structuredContent`. Both E2E transports remove the actual header and parse returned
JSON text, or preserve the function table's Markdown. Their `structuredContent` fields are explicit
test framing; native structured-content propagation is not claimed.

## Tested failures and limitations

The first native engine run passed **11/12** with 179 PDF/TXT pairs: its first-25 preset comparison
failed after custom parent workspace/reference-seed variables were not forwarded into the actual
SDK MCP process. The upstream transport's inherited safe environment list excludes those variables.
Per-call workspace cases passed. The private installed test configuration was corrected **before
Plugin.load**, using the production helper's `--workspace` and explicit reference seed entries in
`mcp.json.env`. The configured rerun passed 12/12 with 255 pairs. The precise error at the old default
workspace was not captured; no particular filesystem error is claimed. Normal users should configure
the helper workspace, explicit MCP environment or per-call workspace rather than assume ambient forwarding.

The first native checker passed **45/47** because two assertions incorrectly expected the SDK's
generated action model to reject an out-of-enum theory source and nonstring override values.
Both were accepted by that model. A characterization rerun passed **48/49**: its assumption that
`shots=[]` would be ignored by `qc-001` was also wrong. The final 49/49 checks instead verify these
actual observations:

- `source="wrong"`, `action="extract"`, nonempty text and an explicit workspace reach the engine,
  return `ok: true`, and are treated as text. Enum enforcement is a **tested failure**.
- `overrides={"shots": []}` reaches the engine for `qc-001`, then returns `ok: false` with
  `Preflight: Unknown/inapplicable preset parameter: shots`. The SDK did not enforce the nested
  string constraint; this inapplicable-parameter failure is not evidence of general type enforcement.
- Raw MCP input schemas preserve the enum and dictionary constraints. The generated SDK action
  fields reduce enum strings to strings and dictionaries to generic dictionaries. The provider-schema
  projection retains the source enum but removes `additionalProperties`. Complete schema fidelity
  and strict action validation therefore remain unsatisfied. No supported strict switch was found.

Final 49/49 is a characterization result, not a claim that these validation gaps were repaired.
The original failed receipts and actual final returned values were retained locally. The approved
engine and SDK were not changed to hide these outcomes.

The first real Conversation attempt failed during helper-agent registration, before a provider
request: its frontmatter `skills` reference did not resolve the plugin-bundled skill through the SDK's
agent registry. The reference was removed and the agent instructions made self-contained. The fixed
Conversation suite passed 14/14. Actual delegation to that helper agent and interactive slash-command
invocation were not exercised; loader/registration and command-to-skill merge were exercised.

Invalid-manifest tests verify fatal rejection of malformed JSON, nonobject manifests, unsupported
schema, invalid name and author. Unknown fields/nonobject extensions can be ignored while loading.
An invalid MCP document/schema disables the MCP component. An invalid absolute/traversing command,
traversing cwd or reserved environment override skips the affected individual server, leaving no server
in the one-server negative fixtures. An unsupported server field skips that server while
a valid sibling survives. These actual outcomes are not described as universal plugin rejection.

## Uncompleted tests

A real model, the full OpenHands CLI/web application or remote runtime, Linux/macOS, another SDK
version, actual Windows `py -3` invocation, interactive slash commands, helper-agent delegation,
clean network SDK bootstrap, retrieval of host attachments/history and visual PDF inspection were
not tested. Attachment/history retrieval is not a plugin capability; tests supplied local files or
confirmed text. Full application coverage must not be inferred from successful SDK Conversation tests.

The handoff kit reports SpinDoctor 3.1.2's C# suite **18/18 with three 29-qubit checks adapted to the
298 limit**, with Russell's approval to publish on that basis. That historical suite was not rerun
for this integration and is separate from the Python/SDK results above.

## Reproduce

Install the external `openhands-sdk==1.54.0` dependency in a Python 3.12+ environment. Put that
interpreter's directory on PATH and set TEMP/TMP to an isolated scratch directory before testing.
Set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUTF8=1`. Run from this repository; replace each
angle-bracket argument with your chosen path. The harnesses create fresh private plugin copies,
explicit MCP workspaces and host persistence. The direct native harness uses public executor timeout
600 seconds and discovery timeout 60 seconds; Conversation harnesses keep the SDK defaults. No
unsupported timeout fields are added to the portable manifest.

```sh
python -B tests/install_check.py <installer-results.json>
python -B tests/native_check.py <native-results.json>
python -B tests/conversation_check.py <conversation-results.json>
python -B tests/e2e_mcp.py --server <absolute-sdk-python-executable> -B tests/native_bridge.py --examples <absolute-engine-examples-theory-directory> --out <native-e2e-results.json>
```

For the full engine suite through genuine Conversation dispatch, substitute
`tests/conversation_bridge.py` for the native bridge. Its tool-list schemas come from the actual
loopback provider request, and each tool execution creates and closes a real Conversation.
The stand-in never needs a remote API key. Ordinary plugin use needs the host's own configured model.

The release inventory contains **60 files**, including **35 engine files byte-identical** to the approved
kit, the complete byte-identical GPL LICENSE, full author/copyright notices and self-contained
validation fixtures. All 32 Python syntax and eight JSON syntax checks pass; the strict private-path
and secret scan is clean. No runtime packages, generated reports or Python caches are bundled.
The original 25 source files remain preserved. Publication readback and fresh-clone testing are recorded separately
after publishing; this file reports prepublication checks.
