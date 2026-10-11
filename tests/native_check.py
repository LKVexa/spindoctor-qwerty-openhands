#!/usr/bin/env python3
# Genuine OpenHands loader, MCP schemas, dispatch and invalid-component outcomes.
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from native_host import NativeHost, RELEASE

home = Path(tempfile.mkdtemp(prefix="spindoctor-openhands-check-"))
os.environ["SPINDOCTOR_WORKSPACE"] = str(home / "workspace")
checks = []
def check(name, passed, detail=None):
    checks.append({"name": name, "pass": bool(passed), **({"detail": detail} if detail is not None else {})})
    print(("PASS " if passed else "FAIL ") + name, flush=True)

host = NativeHost(home)
try:
    from jsonschema import Draft202012Validator
    from openhands.sdk import Plugin
    from openhands.sdk.mcp.definition import MCPToolAction
    from openhands.sdk.plugin.format.base import _load_schema
    plugin = host.plugin
    check("genuine installed SDK is 1.54.0", importlib.metadata.version("openhands-sdk") == "1.54.0")
    check("native loader accepts portable 1.1.0 manifest", plugin.name == "spindoctor-qwerty" and plugin.version == "1.1.0")
    manifest = json.loads((host.root / "plugin.json").read_text(encoding="utf-8"))
    check("manifest author and GPL metadata complete", manifest["author"] == {"name": "RUSSELL PHILIP SMITHSON", "email": "russellsmithson77@outlook.com"} and manifest["license"] == "GPL-3.0-or-later")
    for filename, schemafile in (("plugin.json", "plugin-1.0.0.schema.json"), ("mcp.json", "mcp-1.0.0.schema.json")):
        Draft202012Validator(_load_schema(schemafile)).validate(json.loads((host.root / filename).read_text(encoding="utf-8")))
        check("offline actual SDK schema accepts " + filename, True)
    check("real loader discovers confirmation skill", any(skill.name == "spindoctor-qwerty" and "user's confirmation" in skill.content for skill in plugin.skills))
    check("real loader discovers both client-extension commands", {item.name for item in plugin.commands} == {"qwerty-run", "qwerty-preset"})
    check("real loader discovers helper agent", len(plugin.agents) == 1 and plugin.agents[0].name == "qwerty-helper")
    check("hooks contain no executable actions", json.loads((host.root / "dev.openhands/hooks/hooks.json").read_text())["hooks"] == {})
    server = plugin.mcp_config["spindoctor-qwerty"]
    check("native root expansion points at actual installed engine", server.args[0] == "-B" and Path(server.args[1]).resolve() == host.root / "engine/scripts/spindoctor_mcp.py")
    check("native MCP cwd is writable data outside installation", Path(server.cwd).is_dir() and host.root not in Path(server.cwd).parents)
    check("configured workspace explicitly survives MCP env boundary", server.env["SPINDOCTOR_WORKSPACE"].get_secret_value() == os.environ["SPINDOCTOR_WORKSPACE"])
    check("loader and MCP startup create no engine workspace", not Path(os.environ["SPINDOCTOR_WORKSPACE"]).exists())
    names = {"spindoctor_functions", "spindoctor_run_script", "spindoctor_run_preset", "spindoctor_list_presets", "spindoctor_report", "spindoctor_test_theory"}
    check("genuine connected client exposes exactly six unprefixed tools", set(host.tools) == names and host.client.is_connected())
    check("real MCP schemas preserve required script and theory enum", host.tools["spindoctor_run_script"].mcp_tool.inputSchema["required"] == ["script"] and host.tools["spindoctor_test_theory"].mcp_tool.inputSchema["properties"]["source"]["enum"] == ["file", "text", "chat"])
    functions, text, observation = host.call("spindoctor_functions", {})
    check("actual observation preserves raw Markdown after SDK header", not observation.is_error and text.startswith("## SpinDoctor") and "Function | What it does | Command to type" in text)
    check("SDK observation omits MCP structuredContent", "structuredContent" not in observation.model_dump() and not hasattr(observation, "structured_content"))
    check("native dispatch lists all 241 presets", host.call("spindoctor_list_presets", {})[0]["count"] == 241)
    circuit, _, observation = host.call("spindoctor_run_script", {"script": "q.circuit new nativebell 2\nq.circuit add h 0\nq.circuit add cx 0 1\nq.circuit run shots 1000 basis z"})
    reports = [path for row in circuit["results"] for path in row.get("reports", [])]
    check("native dispatch creates TXT and PDF reports", circuit["ok"] and all(any(p.endswith(extension) and Path(p).is_file() for p in reports) for extension in (".txt", ".pdf")))
    state = host.call("spindoctor_run_script", {"script": "q.circuit result"})[0]
    check("native calls preserve circuit state", state["ok"] and state["results"][0]["result"]["qubits"] == 2)
    report_path = next(p for p in reports if p.endswith(".txt"))
    report = host.call("spindoctor_report", {"name": Path(report_path).name})[0]
    check("native report dispatcher reads persisted TXT report", report["ok"] and "SpinDoctor" in report.get("text", ""))
    invalid, _, observation = host.call("spindoctor_run_script", {"script": "q.invalid"})
    check("engine failure retains JSON and SDK is_error", invalid["ok"] is False and observation.is_error)
    wide, _, observation = host.call("spindoctor_run_script", {"script": "q.circuit new too-wide 299"})
    check("299-qubit request is rejected through genuine dispatcher", wide["ok"] is False and observation.is_error)
    traversal, _, observation = host.call("spindoctor_report", {"name": "../outside.txt"})
    check("report traversal is rejected through genuine dispatcher", traversal["ok"] is False and observation.is_error)
    for label, name, args in (("missing required script", "spindoctor_run_script", {}), ("wrong script type", "spindoctor_run_script", {"script": {}})):
        try:
            host.tools[name].action_from_arguments(args)
        except Exception as error:
            check("native schema rejects " + label, type(error).__name__ == "ValidationError")
        else:
            check("native schema rejects " + label, False)
    enum_action = host.tools["spindoctor_test_theory"].action_from_arguments({"source": "wrong", "action": "extract", "text": "Nonempty theory text."})
    check("SDK partial validator accepts source outside raw MCP enum (known limitation)", enum_action.data["source"] == "wrong")
    enum_result, _, enum_observation = host.call("spindoctor_test_theory", {"source": "wrong", "action": "extract", "text": "Nonempty theory text."})
    check("invalid source reaches engine and is extracted as text (known limitation)", enum_result["ok"] and not enum_observation.is_error and enum_result["extracted"]["source"] == "wrong")
    override_action = host.tools["spindoctor_run_preset"].action_from_arguments({"preset_id": "qc-001", "overrides": {"shots": []}})
    check("SDK partial validator accepts nonstring override value (known limitation)", override_action.data["overrides"]["shots"] == [])
    override_result, _, override_observation = host.call("spindoctor_run_preset", {"preset_id": "qc-001", "overrides": {"shots": []}})
    check("nonstring shots override reaches engine and produces an error", override_result["ok"] is False and override_observation.is_error, override_result.get("error"))
    observation = host.tools["spindoctor_run_script"](MCPToolAction(data={"script": {}}))
    check("direct malformed SDK action returns error observation", observation.is_error)
    theory = host.call("spindoctor_test_theory", {"source": "chat", "text": "Confirmed summary: H on zero gives equal outcomes.", "hypothesis": "H gives half ones", "prediction": "P(1)=0.5", "script": "q.circuit new theory 1\nq.circuit add h 0\nq.circuit run shots 4000 basis z", "checks": [{"kind": "probability", "outcome": "1", "expected": 0.5, "tolerance": 0.05}]})[0]
    check("native confirmed-chat theory creates supported PDF report", theory["verdict"] == "supported" and any(p.endswith(".pdf") for p in theory["reports"]))
    check("native preset dispatch succeeds with configured workspace", host.call("spindoctor_run_preset", {"preset_id": "qc-001"})[0]["ok"])

    def variant(label, file, transform, fatal=False, expected_servers=None):
        target = home / "variants" / label
        shutil.copytree(host.root, target)
        destination = target / file
        value = json.loads(destination.read_text(encoding="utf-8"))
        replacement = transform(value)
        destination.write_text(replacement if isinstance(replacement, str) else json.dumps(replacement), encoding="utf-8")
        try:
            loaded = Plugin.load(target)
        except ValueError:
            check("native invalid component: " + label, fatal, "fatal manifest rejection")
        else:
            passed = not fatal and (expected_servers is None or set(loaded.mcp_config) == expected_servers)
            check("native invalid component: " + label, passed, "loaded plugin; MCP servers=" + ",".join(loaded.mcp_config))

    def field(name, value):
        return lambda data: dict(data, **{name: value})
    variant("manifest-bad-json", "plugin.json", lambda data: "{", fatal=True)
    variant("manifest-non-object", "plugin.json", lambda data: [], fatal=True)
    variant("manifest-unsupported-schema", "plugin.json", field("$schema", "unsupported"), fatal=True)
    variant("manifest-invalid-name", "plugin.json", field("name", "bad_name"), fatal=True)
    variant("manifest-invalid-author", "plugin.json", field("author", "wrong"), fatal=True)
    variant("manifest-unknown-field", "plugin.json", field("ignoredExample", "ignored"), expected_servers={"spindoctor-qwerty"})
    variant("manifest-non-object-extensions", "plugin.json", field("extensions", []), expected_servers={"spindoctor-qwerty"})
    variant("mcp-bad-json", "mcp.json", lambda data: "{", expected_servers=set())
    variant("mcp-unsupported-schema", "mcp.json", field("$schema", "unsupported"), expected_servers=set())
    def server_change(name, value, sibling=False):
        def mutate(data):
            data["mcpServers"]["spindoctor-qwerty"][name] = value
            if sibling:
                data["mcpServers"]["valid-sibling"] = json.loads((host.root / "mcp.json").read_text())["mcpServers"]["spindoctor-qwerty"]
            return data
        return mutate
    variant("mcp-absolute-command", "mcp.json", server_change("command", sys.executable), expected_servers=set())
    variant("mcp-cwd-traversal", "mcp.json", server_change("cwd", "${PLUGIN_ROOT}/../../outside"), expected_servers=set())
    variant("mcp-command-traversal", "mcp.json", server_change("command", "./../../outside"), expected_servers=set())
    variant("mcp-reserved-env", "mcp.json", server_change("env", {"PLUGIN_ROOT": "forbidden"}), expected_servers=set())
    variant("mcp-unsupported-extra-with-sibling", "mcp.json", server_change("timeout", 600, sibling=True), expected_servers={"valid-sibling"})
    check("no Python cache files generated in source or installed copy", not any(p.name == "__pycache__" or p.suffix in (".pyc", ".pyo") for root in (RELEASE, host.root) for p in root.rglob("*")))
finally:
    host.close()
check("genuine MCP client closes its connection", host.client._closed and not host.client.is_connected())
summary = {"host": "OpenHands SDK 1.54.0", "python": sys.version.split()[0], "passed": sum(row["pass"] for row in checks), "total": len(checks), "checks": checks, "profile": str(home), "constraintLimitations": {"sourceOutsideEnum": enum_result, "nonstringOverride": override_result}, "boundary": "Genuine portable plugin loader, connected SDK MCP tools and native schema/action/observation handling. Known enum/nested override validation gaps are observed, not treated as enforcement successes. No model or interactive application."}
if len(sys.argv) > 1:
    target = Path(sys.argv[1]); target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2), flush=True)
sys.exit(0 if summary["passed"] == summary["total"] else 1)
