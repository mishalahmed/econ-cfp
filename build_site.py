"""Builds the GitHub Pages copy of the CFP dashboard into _site/.

Combines data/sources.json, data/calls/*.json and the latest run logs into a single data.json
(the same shape the local dashboard server returns from /api/data, without the user's marks).
"""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "_site"


def read_json(path, errors):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        errors.append(f"{path.relative_to(ROOT).as_posix()}: {exc}")
        return None


def main():
    errors = []
    sources = read_json(DATA / "sources.json", errors) if (DATA / "sources.json").exists() else None
    calls = [c for c in (read_json(p, errors) for p in sorted((DATA / "calls").glob("*.json"))) if isinstance(c, dict)]
    run_files = sorted((DATA / "runs").glob("*.json"), reverse=True)[:15]
    runs = [r for r in (read_json(p, errors) for p in run_files) if isinstance(r, dict)]

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for name in ("index.html",):
        if (ROOT / name).exists():
            shutil.copy2(ROOT / name, OUT / name)
    payload = {
        "server_time": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "calls": calls,
        "runs": runs,
        "marks": {},
        "errors": [e.split(":")[0] for e in errors],
    }
    (OUT / "data.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    for e in errors:
        print("WARNING:", e)
    print(f"Built _site: {len(calls)} calls, {len(runs)} runs, {len(errors)} unreadable file(s).")


if __name__ == "__main__":
    main()
