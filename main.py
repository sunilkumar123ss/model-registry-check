"""Validate local artifact integrity and a small model-registry manifest."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys


def verify(manifest, artifact_root):
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")
    root = Path(artifact_root).resolve()
    entries = manifest["entries"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("entries must be a nonempty list")
    seen, production, verified = set(), {}, []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each registry entry must be an object")
        name, version, stage = entry["name"], entry["version"], entry["stage"]
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", name):
            raise ValueError("name must be a lowercase model identifier")
        if not isinstance(version, str) or not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
            raise ValueError("version must have three nonnegative semantic-version components")
        if (name, version) in seen:
            raise ValueError("duplicate name/version")
        seen.add((name, version))
        if stage not in ("draft", "staging", "production"):
            raise ValueError("unknown stage")
        relative = Path(entry["artifact"])
        path = (root / relative).resolve()
        if relative.is_absolute() or root not in path.parents:
            raise ValueError("artifact must remain inside artifact_root")
        if not path.is_file():
            raise ValueError("artifact is not a regular file")
        expected = entry["sha256"]
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError("sha256 must be 64 lowercase hex digits")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected:
            raise ValueError(f"checksum mismatch for {name}@{version}")
        if stage == "production":
            if name in production:
                raise ValueError("only one production version per model is allowed")
            evaluation = entry.get("evaluation", {})
            if not isinstance(evaluation, dict):
                raise ValueError("evaluation must be an object")
            metrics = evaluation.get("metrics", {})
            if not isinstance(evaluation.get("dataset"), str) or not evaluation["dataset"] or not isinstance(metrics, dict) or not metrics:
                raise ValueError("production entries require dataset identity and evaluation metrics")
            if any(type(v) not in (int, float) or not math.isfinite(v) for v in metrics.values()):
                raise ValueError("evaluation metrics must be finite numbers")
            production[name] = version
        verified.append({"name": name, "version": version, "stage": stage, "sha256": digest})
    return {"valid": True, "verified": verified, "production": production}

