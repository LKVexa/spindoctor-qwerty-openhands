#!/usr/bin/env python3
# Test transport through genuine OpenHands Conversation and loopback model protocol.
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import sys
from conversation_host import ConversationHost

protocol = sys.stdout
sys.stdout = sys.stderr
host = ConversationHost()
names = {"spindoctor_functions", "spindoctor_run_script", "spindoctor_run_preset", "spindoctor_list_presets", "spindoctor_report", "spindoctor_test_theory"}
try:
    for line in sys.stdin:
        if not line.strip():
            continue
        message = None
        try:
            message = json.loads(line)
            if "id" not in message:
                continue
            if message["method"] == "initialize":
                result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "spindoctor-openhands-conversation-test-bridge", "version": "1.1.0"}}
            elif message["method"] == "tools/list":
                if not host.provider_requests:
                    host.call("spindoctor_functions", {})
                schemas = host.provider_requests[0]["schemas"]
                result = {"tools": [{"name": item["function"]["name"], "description": item["function"].get("description", ""), "inputSchema": item["function"]["parameters"]} for item in schemas if item["function"]["name"] in names]}
            elif message["method"] == "tools/call":
                params = message["params"]
                value, text, observation = host.call(params["name"], params.get("arguments") or {})
                result = {"content": [{"type": "text", "text": text}], "structuredContent": value, "isError": observation.is_error}
            else:
                raise ValueError("Unsupported test transport method")
            response = {"jsonrpc": "2.0", "id": message["id"], "result": result}
        except Exception as error:
            response = {"jsonrpc": "2.0", "id": message.get("id") if isinstance(message, dict) else None, "error": {"code": -32000, "message": str(error)}}
        protocol.write(json.dumps(response, ensure_ascii=False) + "\n")
        protocol.flush()
finally:
    host.close()
