"""Write each file's first line from the latest release on uxplima.com.

Plugins released before uxmCore read these files to tell operators about updates. They keep doing so for as
long as old jars run, so the files must follow the store. A file is only ever rewritten with a version the store
answered; any failure leaves it as it is, because some old readers break on an empty or missing line.

    python .github/sync_versions.py
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

API = "https://www.uxplima.com/v1/catalog/products/{ref}/versions/latest"
VERSION = re.compile(r"^\d+(\.\d+)*$")

# File name -> product number on uxplima.com.
FILES = {
    "ancBlacksmith": 87,
    "ancSpawners": 150,
    "uxmClaims": 154,
    "uxmDiscordSync": 86,
    "uxmDiscordSyncRecode": 86,
    "uxmDragonEvent": 158,
    "uxmFarmer": 153,
    "uxmHelperNPC": 129,
    "uxmSupplyRush": 148,
}
# sFarmer's readers show the whole line, which names the uxmFarmer version.
SFARMER = ("sFarmer", 153)


def latest(ref: int) -> str | None:
    request = urllib.request.Request(
        API.format(ref=ref),
        headers={"Accept": "application/json", "User-Agent": "UXPluginVersions-sync"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.load(response)["data"]
    except (OSError, ValueError, KeyError, TypeError) as failure:
        print(f"product {ref}: no answer ({failure})", file=sys.stderr)
        return None
    version = (data.get("latest") or {}).get("version")
    if not isinstance(version, str) or not VERSION.match(version):
        print(f"product {ref}: unusable version {version!r}", file=sys.stderr)
        return None
    return version


def sync(root: Path) -> list[str]:
    changed = []
    answers: dict[int, str | None] = {}
    for name, ref in FILES.items():
        version = answers.setdefault(ref, latest(ref))
        path = root / name
        current = path.read_text(encoding="utf-8").splitlines()[:1] if path.exists() else []
        if version is None or current == [version]:
            continue
        # Lines after the first describe the release they were written for, so they go with it.
        path.write_text(version + "\n", encoding="utf-8")
        changed.append(f"{name} {version}")

    name, ref = SFARMER
    version = answers.setdefault(ref, latest(ref))
    path = root / name
    if version is not None and path.exists():
        text = path.read_text(encoding="utf-8")
        updated = re.sub(r"Latest version: \S+", f"Latest version: {version}", text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed.append(f"{name} {version}")
    return changed


if __name__ == "__main__":
    for line in sync(Path(__file__).resolve().parent.parent):
        print(line)
