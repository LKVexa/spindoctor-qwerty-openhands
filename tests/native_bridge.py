#!/usr/bin/env python3
# Test transport around genuine OpenHands SDK loading, schemas and MCP dispatch.
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import sys
from native_host import NativeHost

protocol = sys.stdout
sys.stdout = sys.stderr
host = NativeHost()
try:
    for line in sys.stdin:
        if not line.strip():
            continue
        message = None
        try:
            message = json.loads(line)
            if "id" not in message:
                continue
            method = message.get("method")
            if method == "initialize":
                result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "spindoctor-openhands-sdk-test-bridge", "version": "1.1.0"}}
            elif method == "tools/list":
                result = {"tools": [tool.mcp_tool.model_dump(by_alias=True, exclude_none=True) for tool in host.tools.values()]}
            elif method == "tools/call":
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
