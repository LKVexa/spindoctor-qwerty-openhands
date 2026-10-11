#!/usr/bin/env python3
# Fresh-copy preservation, portable interpreter and workspace configuration tests.
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

RELEASE = Path(__file__).resolve().parents[1]
INSTALLER = RELEASE / "tools/install_openhands.py"
home = Path(tempfile.mkdtemp(prefix="spindoctor-openhands-install-check-"))
checks = []
def check(name, passed):
    checks.append({"name": name, "pass": bool(passed)})
    print(("PASS " if passed else "FAIL ") + name)
def run(target, *args):
    return subprocess.run([sys.executable, "-B", str(INSTALLER), "--target", str(target)] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1"))
def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}

try:
    target = home / "installed with spaces"
    workspace = home / "reports outside plugin"
    result = run(target, "--workspace", str(workspace))
    check("fresh installation accepts spaces and creates no engine workspace", result.returncode == 0 and target.is_dir() and not workspace.exists())
    config = json.loads((target / "mcp.json").read_text())
    server = config["mcpServers"]["spindoctor-qwerty"]
    check("workspace is explicit absolute MCP environment configuration", server["env"]["SPINDOCTOR_WORKSPACE"] == str(workspace.resolve()))
    check("portable executable and script args remain separate", server["command"] == "python" and server["args"] == ["-B", "${PLUGIN_ROOT}/engine/scripts/spindoctor_mcp.py"])
    check("cache suppression is explicit in command and environment", "-B" in server["args"] and server["env"]["PYTHONDONTWRITEBYTECODE"] == "1" and server["env"]["PYTHONUTF8"] == "1")
    engine = inventory(target / "engine")
    check("all 35 installed engine files match source bytes", len(engine) == 35 and engine == inventory(RELEASE / "engine"))
    check("full GPL license is copied byte-for-byte", (target / "LICENSE").read_bytes() == (RELEASE / "LICENSE").read_bytes())
    manifest = json.loads((target / "plugin.json").read_text())
    check("version GPL and author metadata remain intact", manifest["version"] == "1.1.0" and manifest["license"] == "GPL-3.0-or-later" and manifest["author"] == {"name": "RUSSELL PHILIP SMITHSON", "email": "russellsmithson77@outlook.com"})
    check("portable skill and client extension components are copied", (target / "skills/spindoctor-qwerty/SKILL.md").is_file() and (target / "dev.openhands/commands/qwerty-run.md").is_file() and (target / "dev.openhands/agents/qwerty-helper.md").is_file())
    before = inventory(target)
    check("existing installed target is preserved without overwrite", run(target).returncode != 0 and inventory(target) == before)
    occupied = home / "occupied"
    occupied.mkdir()
    (occupied / "keep.txt").write_text("existing chat files")
    check("unrelated existing files are preserved", run(occupied).returncode != 0 and inventory(occupied) == {"keep.txt": hashlib.sha256(b"existing chat files").hexdigest()})
    empty = home / "empty-but-existing"
    empty.mkdir()
    check("even an existing empty target is left untouched", run(empty).returncode != 0 and not list(empty.iterdir()))
    nested = RELEASE / "forbidden-test-install"
    check("installation inside release checkout rejects before writes", run(nested).returncode != 0 and not nested.exists())
    absolute = home / "bad-absolute-command"
    check("absolute interpreter command is rejected before writes", run(absolute, "--python-command", sys.executable).returncode != 0 and not absolute.exists())
    shell = home / "bad-shell-command"
    check("shell-style interpreter command is rejected before writes", run(shell, "--python-command", "python -B").returncode != 0 and not shell.exists())
    placeholders = home / "bad-interpreter-placeholder"
    check("interpreter placeholder arguments are rejected before writes", run(placeholders, "--python-arg=${UNSUPPORTED}").returncode != 0 and not placeholders.exists())
    inside = home / "bad-internal-workspace"
    check("workspace inside installed plugin rejects before writes", run(inside, "--workspace", str(inside / "workspace")).returncode != 0 and not inside.exists())
    windows = home / "windows-py"
    result = run(windows, "--python-command", "py", "--python-arg=-3")
    command = json.loads((windows / "mcp.json").read_text())["mcpServers"]["spindoctor-qwerty"]
    check("Windows launcher helper uses bare py with separate -3 and -B args", result.returncode == 0 and command["command"] == "py" and command["args"] == ["-3", "-B", "${PLUGIN_ROOT}/engine/scripts/spindoctor_mcp.py"])
    check("copied payload excludes git metadata and Python caches", not any(p.name in (".git", "__pycache__") or p.suffix in (".pyc", ".pyo") for p in target.rglob("*")))
    summary = {"python": sys.version.split()[0], "passed": sum(row["pass"] for row in checks), "total": len(checks), "checks": checks}
    if len(sys.argv) > 1:
        receipt = Path(sys.argv[1]); receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    status = 0 if summary["passed"] == summary["total"] else 1
finally:
    if home.resolve().parent != Path(tempfile.gettempdir()).resolve() or not home.name.startswith("spindoctor-openhands-install-check-"):
        raise RuntimeError("Unsafe test cleanup path")
    shutil.rmtree(home)
sys.exit(status)
