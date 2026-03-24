#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


def export_state(output: Path):
    root = Path.cwd()
    payload = {
        "component": "task-workflow",
        "exported_at": datetime.now().isoformat(),
        "artifacts": {
            "config_cron": str((root / "config" / "cron.yaml").exists()),
            "references": sorted([str(p.relative_to(root)) for p in (root / "references").glob("*.md")]) if (root / "references").exists() else [],
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def import_state(input_path: Path):
    _ = json.loads(input_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="task-workflow stack contract helper")
    sub = parser.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("export")
    ex.add_argument("--output", required=True)
    im = sub.add_parser("import")
    im.add_argument("--input", required=True)
    args = parser.parse_args()
    if args.cmd == "export":
        export_state(Path(args.output))
    else:
        import_state(Path(args.input))
