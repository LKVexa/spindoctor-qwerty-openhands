# Genuine OpenHands SDK plugin loader and MCP dispatcher, used by test harnesses.
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

RELEASE = Path(__file__).resolve().parents[1]

def isolate(home):
    home = Path(home).resolve()
    for key, folder in {"OH_PERSISTENCE_DIR": "persistence", "LOG_DIR": "logs", "TIKTOKEN_CACHE_DIR": "tokens", "XDG_CACHE_HOME": "cache", "TEMP": "temp", "TMP": "temp"}.items():
        destination = home / folder
        destination.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(destination)
    os.environ.update(LOG_LEVEL="WARNING", LOG_TO_FILE="false", DEBUG_LLM="false", OPENHANDS_SUPPRESS_BANNER="1", LITELLM_LOCAL_MODEL_COST_MAP="true", PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
    os.environ["PATH"] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", "")

def install_copy(home, forward_environment=True):
    target = Path(home) / "installed-plugin"
    command = [sys.executable, "-B", str(RELEASE / "tools/install_openhands.py"), "--target", str(target)]
    if forward_environment and os.environ.get("SPINDOCTOR_WORKSPACE"):
        command += ["--workspace", os.environ["SPINDOCTOR_WORKSPACE"]]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    # MCP's safe inherited environment omits custom variables. Reference seeds are test config.
    if forward_environment:
        config = target / "mcp.json"
        settings = json.loads(config.read_text(encoding="utf-8"))
        env = settings["mcpServers"]["spindoctor-qwerty"]["env"]
        env.update({key: os.environ[key] for key in ("SPINDOCTOR_MEASUREMENT_SEED", "SPINDOCTOR_FIELD_SEED") if key in os.environ})
        config.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    return target

class NativeHost:
    def __init__(self, home=None, forward_environment=True):
        self.home = Path(home) if home else Path(tempfile.mkdtemp(prefix="spindoctor-openhands-native-"))
        isolate(self.home)
        self.root = install_copy(self.home, forward_environment)
        from openhands.sdk import Plugin, create_mcp_tools
        self.plugin = Plugin.load(self.root)
        self.client = create_mcp_tools(self.plugin.mcp_config, timeout=60.0)
        self.client.__enter__()
        self.tools = {tool.name: tool for tool in self.client.tools}
        for tool in self.tools.values():
            tool.executor.timeout = 600

    def call(self, name, arguments):
        tool = self.tools[name]
        observation = tool(tool.action_from_arguments(arguments))
        header = "[Tool '" + name + "' executed.]"
        texts = [block.text for block in observation.content if hasattr(block, "text")]
        output = "\n".join(text for text in texts if text != header)
        result = {"ok": not observation.is_error, "markdown": output} if name.endswith("spindoctor_functions") else json.loads(output)
        return result, output, observation

    def close(self):
        self.client.__exit__(None, None, None)
