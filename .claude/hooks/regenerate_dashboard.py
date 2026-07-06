#!/usr/bin/env python3
"""Hook PostToolUse : régénère les pages HTML si timeline.json/apps.json/help.json vient d'être édité."""

import json
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent.parent
WATCHED_SUFFIXES = ("timeline.json", "apps.json", "help.json")


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    if not isinstance(data, dict):
        return

    tool_input = data.get("tool_input") or {}
    tool_response = data.get("tool_response") or {}
    file_path = tool_input.get("file_path") or tool_response.get("filePath") or ""

    if not any(str(file_path).endswith(suffix) for suffix in WATCHED_SUFFIXES):
        return

    try:
        subprocess.run(
            [sys.executable, "generate_dashboard.py"],
            cwd=str(REPO_DIR),
            capture_output=True,
            timeout=30,
        )
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
