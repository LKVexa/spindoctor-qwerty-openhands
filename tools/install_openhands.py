#!/usr/bin/env python3
# SpinDoctor Qwerty 1.1.0 - fresh-copy OpenHands configuration helper
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Create a separate installation without replacing existing files or host profiles."""
import argparse
import json
from pathlib import Path
import re
import sys

SOURCE = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="New plugin directory outside the checkout")
    parser.add_argument("--python-command", default="python", help="Bare executable on host PATH; e.g. python3 or py")
    parser.add_argument("--python-arg", action="append", default=[])
    parser.add_argument("--workspace", help="Optional persistent report directory outside the installation")
    options = parser.parse_args()
    target = Path(options.target).resolve()
    try:
        if target.exists():
            raise ValueError("Destination already exists; preserving all files. Choose a new directory.")
        if target == SOURCE or SOURCE in target.parents or target in SOURCE.parents:
            raise ValueError("Choose a destination separate from the release checkout")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", options.python_command):
            raise ValueError("Agent Plugins requires a bare executable name; put its directory on host PATH")
        if any("${" in arg for arg in options.python_arg):
            raise ValueError("Interpreter arguments must be literal strings")
        payload = {}
        for item in sorted(SOURCE.rglob("*")):
            relative = item.relative_to(SOURCE)
            if any(part in (".git", "__pycache__", "node_modules") for part in relative.parts) or item.suffix in (".pyc", ".pyo"):
                continue
            if item.is_symlink():
                raise ValueError("Symlinks are not supported in the installation payload")
            if item.is_file():
                payload[relative] = item.read_bytes()
        settings = json.loads(payload[Path("mcp.json")].decode("utf-8"))
        server = settings["mcpServers"]["spindoctor-qwerty"]
        server["command"] = options.python_command
        server["args"] = options.python_arg + ["-B", "${PLUGIN_ROOT}/engine/scripts/spindoctor_mcp.py"]
        if options.workspace:
            workspace = Path(options.workspace).resolve()
            if workspace == target or target in workspace.parents:
                raise ValueError("Workspace must remain outside the installed plugin")
            server["env"]["SPINDOCTOR_WORKSPACE"] = str(workspace)
        payload[Path("mcp.json")] = (json.dumps(settings, indent=2) + "\n").encode("utf-8")
        target.mkdir(parents=True, exist_ok=False)
        for relative, data in payload.items():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        print("Created SpinDoctor 1.1.0 plugin in " + str(target))
        print("Load this directory with OpenHands PluginSource. Existing profiles and files were preserved.")
        return 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        print("Installation stopped: " + str(error), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
