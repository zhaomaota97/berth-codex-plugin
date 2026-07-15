#!/usr/bin/env python3
"""Repository-level validation entrypoint."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "agentour-compiler"


def main() -> int:
    manifest = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text())
    market = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text())
    assert manifest["name"] == "agentour-compiler"
    assert market["name"] == "agentour-platform"
    assert any(item["name"] == manifest["name"] for item in market["plugins"])
    assert (PLUGIN / "skills" / "agentour-compiler" / "SKILL.md").is_file()
    assert (PLUGIN / "scripts" / "agentour_api.py").is_file()
    assert (PLUGIN / "scripts" / "validate_package.py").is_file()
    assert (PLUGIN / "scripts" / "fidelity_report.py").is_file()
    codex_home = pathlib.Path(os.environ.get("CODEX_HOME", pathlib.Path.home() / ".codex"))
    validator = codex_home / "skills" / ".system" / "plugin-creator" / "scripts" / "validate_plugin.py"
    if validator.is_file():
        result = subprocess.run([sys.executable, str(validator), str(PLUGIN)])
        return result.returncode
    print("Repository checks passed (Codex plugin validator is not installed in CODEX_HOME)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
