#!/usr/bin/env python3
"""Calculate and validate a Agentour migration fidelity report."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from datetime import datetime, timezone


WEIGHTS = {
    "task_semantics": 0.30,
    "capabilities_tools": 0.20,
    "instructions_rules": 0.15,
    "outputs_artifacts": 0.15,
    "workflow_approvals": 0.10,
    "multi_turn": 0.05,
    "performance_resources": 0.05,
}


def package_hash(root: pathlib.Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel.startswith(("node_modules/", ".git/")):
            continue
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def calculate(report: dict) -> tuple[int | None, str]:
    assertions = report.get("critical_assertions") or {}
    if int(assertions.get("failed", 0)) > 0:
        return None, "D"
    dimensions = report.get("dimensions") or {}
    if any(dimensions.get(key) is None for key in WEIGHTS):
        return None, "unverified"
    values = {key: float(dimensions[key]) for key in WEIGHTS}
    if any(value < 0 or value > 100 for value in values.values()):
        raise ValueError("dimension scores must be between 0 and 100")
    score = round(sum(values[key] * weight for key, weight in WEIGHTS.items()))
    if score >= 90:
        return score, "A"
    if score >= 80:
        return score, "B"
    if score >= 60:
        return score, "C"
    return score, "D"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package")
    parser.add_argument("report")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    package = pathlib.Path(args.package).resolve()
    report_path = pathlib.Path(args.report).resolve()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    score, grade = calculate(report)
    current_hash = package_hash(package)
    old_hash = report.get("package_sha256")
    if old_hash and old_hash != current_hash and not args.write:
        raise SystemExit("fidelity report is stale: Package hash changed")
    report["package_sha256"] = current_hash
    report["score"] = score
    report["grade"] = grade
    report["verified_at"] = datetime.now(timezone.utc).isoformat()
    if args.write:
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"score": score, "grade": grade, "package_sha256": current_hash}, indent=2))
    if grade in {"C", "D", "unverified"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
