#!/usr/bin/env python3
# Genuine OpenHands Conversation plugin merge, provider schemas and tool execution.
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
import json
from pathlib import Path
import sys
from conversation_host import ConversationHost

checks = []
def check(name, passed, detail=None):
    checks.append({"name": name, "pass": bool(passed), **({"detail": detail} if detail is not None else {})})
    print(("PASS " if passed else "FAIL ") + name, flush=True)
host = ConversationHost(use_incoming_workspace=False)
try:
    functions, text, observation = host.call("spindoctor_functions", {})
    check("genuine Conversation dispatch preserves raw function Markdown", not observation.is_error and text.startswith("## SpinDoctor") and "Function | What it does | Command to type" in text)
    skills = host.last_conversation.agent.agent_context.skills
    check("genuine Conversation merges confirmation skill", any(skill.name == "spindoctor-qwerty" and "user's confirmation" in skill.content for skill in skills))
    check("genuine Conversation converts both extension commands to skills", {"spindoctor-qwerty:qwerty-run", "spindoctor-qwerty:qwerty-preset"}.issubset({skill.name for skill in skills}))
    names = {"spindoctor_functions", "spindoctor_run_script", "spindoctor_run_preset", "spindoctor_list_presets", "spindoctor_report", "spindoctor_test_theory"}
    advertised = host.provider_requests[0]["schemas"]
    check("actual loopback provider request advertises all six MCP tools", names.issubset({item["function"]["name"] for item in advertised}))
    check("SDK observation boundary omits structuredContent", "structuredContent" not in observation.model_dump())
    check("genuine Conversation lists all 241 presets", host.call("spindoctor_list_presets", {})[0]["count"] == 241)
    circuit = host.call("spindoctor_run_script", {"script": "q.circuit new conversationbell 2\nq.circuit add h 0\nq.circuit add cx 0 1\nq.circuit run shots 1000 basis z"})[0]
    reports = [p for row in circuit["results"] for p in row.get("reports", [])]
    check("genuine Conversation creates TXT and PDF reports", circuit["ok"] and all(any(p.endswith(extension) and Path(p).is_file() for p in reports) for extension in (".txt", ".pdf")))
    state = host.call("spindoctor_run_script", {"script": "q.circuit result"})[0]
    check("separate genuine Conversations retain configured workspace state", state["ok"] and state["results"][0]["result"]["qubits"] == 2)
    report = host.call("spindoctor_report", {"name": Path(next(p for p in reports if p.endswith(".txt"))).name})[0]
    check("genuine Conversation reads an actual TXT report", report["ok"] and "spindoctor" in report["text"].lower())
    check("genuine Conversation preset dispatch succeeds", host.call("spindoctor_run_preset", {"preset_id": "qc-001"})[0]["ok"])
    theory = host.call("spindoctor_test_theory", {"source": "chat", "text": "Confirmed test summary: H on zero gives equal outcomes.", "hypothesis": "H gives half ones", "prediction": "P(1)=0.5", "script": "q.circuit new theory 1\nq.circuit add h 0\nq.circuit run shots 4000 basis z", "checks": [{"kind": "probability", "outcome": "1", "expected": 0.5, "tolerance": 0.05}]})[0]
    check("genuine Conversation confirmed-chat theory creates supported PDF", theory["verdict"] == "supported" and any(p.endswith(".pdf") and Path(p).is_file() for p in theory["reports"]))
    invalid, _, observation = host.call("spindoctor_run_script", {"script": "q.invalid"})
    check("genuine Conversation retains engine failure and is_error", invalid["ok"] is False and observation.is_error)
    check("actual tool action and observation events are recorded", any(type(event).__name__ == "ActionEvent" and getattr(event, "tool_name", None) in names for event in host.events) and any(type(event).__name__ == "ObservationEvent" and getattr(event, "tool_name", None) in names for event in host.events))
    check("loopback stand-in finishes native turns without provider errors", not host.provider_errors and host.closed_conversations == 8 and any(item["completed"] for item in host.provider_requests), host.provider_errors)
    summary = {"host": "OpenHands SDK 1.54.0", "python": sys.version.split()[0], "passed": sum(row["pass"] for row in checks), "total": len(checks), "checks": checks, "profile": str(host.home), "providerRequests": len(host.provider_requests), "closedConversations": host.closed_conversations,
               "boundary": "Genuine SDK Conversation loads portable plugin, merges skills, advertises schemas and dispatches real MCP engine tools. Loopback protocol stand-in chooses tools/arguments; no real model or interactive application."}
    if len(sys.argv) > 1:
        target = Path(sys.argv[1]); target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
    sys.exit(0 if summary["passed"] == summary["total"] else 1)
finally:
    host.close()
