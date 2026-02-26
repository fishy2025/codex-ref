from __future__ import annotations

from pathlib import Path


def load_simple_yaml(path: str | Path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    cleaned = []
    for raw in lines:
        line = raw.split("#", 1)[0].rstrip()
        if line.strip():
            cleaned.append(line)

    if not cleaned:
        return None

    if all(line.lstrip().startswith("-") for line in cleaned):
        result = []
        for line in cleaned:
            value = line.split("-", 1)[1].strip()
            result.append(value)
        return result

    data = {}
    for line in cleaned:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.isdigit():
            data[key] = int(value)
        else:
            data[key] = value
    return data
