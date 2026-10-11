"""Checks data/sources.json, data/calls/*.json and data/runs/*.json against the format in AGENT.md.

Prints one line per problem and a summary line. Exit code 0 even when problems are found, so the
Pages build still publishes; run `python3 validate.py --strict` to get exit code 1 on problems.
"""
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

FIELDS = {"General", "Agricultural", "Behavioral & Experimental", "Development", "Econometrics", "Economic History",
          "Education", "Environmental", "Finance", "Health", "IO", "Labor", "Macro & Monetary", "Political Economy",
          "Public", "Theory", "Trade", "Urban & Transport"}
REGIONS = {"US", "Canada", "Europe", "Far East", "Australia & NZ", "Rotating"}
KEYS = ["id", "series_id", "status", "name", "edition", "organizer", "fields", "region", "city", "country", "venue",
        "conf_start", "conf_end", "conf_dates_note", "format", "call_type", "deadline", "deadline_time", "deadline_tz",
        "deadline_note", "full_paper_required", "submission_requirements", "submission_fee", "registration_fee",
        "registration_fee_usd", "registration_deadline", "membership_required", "notification_date", "keynotes",
        "journal", "submit_url", "cfp_url", "contact", "source_url", "first_seen", "last_verified", "updated_at",
        "change_kind", "history", "expected_deadline", "expected_note", "last_edition"]
FAR_EAST = {"Japan", "South Korea", "Taiwan", "Hong Kong", "Singapore"}
OUT_OF_SCOPE = {"China", "India", "Macau", "Thailand", "Malaysia", "Indonesia", "Vietnam", "Philippines", "Cambodia",
                "Brazil", "Mexico", "Chile", "Colombia", "Argentina", "Peru", "South Africa", "Israel", "Turkey",
                "United Arab Emirates", "Qatar", "Saudi Arabia", "Morocco", "Egypt"}
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")

problems = []


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        problems.append(f"{path.relative_to(ROOT).as_posix()}: invalid JSON: {exc}")
        return None


def main():
    series = {}
    src = load(DATA / "sources.json")
    for s in (src or {}).get("series", []):
        sid = s.get("series_id")
        if not sid:
            problems.append(f"sources.json: series without series_id ({s.get('name')})")
            continue
        if sid in series:
            problems.append(f"sources.json: duplicate series_id {sid}")
        series[sid] = s
        for f in s.get("fields") or []:
            if f not in FIELDS:
                problems.append(f"sources.json: {sid}: unknown field '{f}'")

    cutoff = (date.today() - timedelta(days=60)).isoformat()
    n = 0
    for path in sorted((DATA / "calls").glob("*.json")):
        c = load(path)
        if not isinstance(c, dict):
            continue
        n += 1
        name = path.name
        missing = [k for k in KEYS if k not in c]
        extra = [k for k in c if k not in KEYS]
        if missing:
            problems.append(f"{name}: missing keys: {', '.join(missing)}")
        if extra:
            problems.append(f"{name}: unexpected keys: {', '.join(extra)}")
        if f"{c.get('id')}.json" != name:
            problems.append(f"{name}: id '{c.get('id')}' does not match the file name")
        if c.get("status") not in ("announced", "expected"):
            problems.append(f"{name}: status must be announced or expected, not '{c.get('status')}'")
        if c.get("change_kind") not in ("seed", "new", "changed", "expected"):
            problems.append(f"{name}: bad change_kind '{c.get('change_kind')}'")
        if not c.get("fields"):
            problems.append(f"{name}: fields is empty")
        for f in c.get("fields") or []:
            if f not in FIELDS:
                problems.append(f"{name}: unknown field '{f}'")
        if c.get("region") not in REGIONS:
            problems.append(f"{name}: bad region '{c.get('region')}'")
        for k in ("conf_start", "conf_end", "deadline", "expected_deadline", "first_seen", "last_verified", "updated_at"):
            v = c.get(k)
            if v is not None and not ISO.match(str(v)):
                problems.append(f"{name}: {k} is not YYYY-MM-DD: '{v}'")
        if c.get("status") == "expected" and not c.get("expected_deadline"):
            problems.append(f"{name}: expected record without expected_deadline")
        country = c.get("country")
        if country:
            if c.get("region") == "Far East" and country not in FAR_EAST:
                problems.append(f"{name}: region Far East but country '{country}'")
            if country in OUT_OF_SCOPE:
                problems.append(f"{name}: venue country '{country}' is outside the dashboard regions")
        if c.get("series_id") not in series:
            problems.append(f"{name}: series_id '{c.get('series_id')}' is not in sources.json")
        if c.get("conf_end") and str(c["conf_end"]) < cutoff:
            problems.append(f"{name}: conference ended more than 60 days ago; move to data/archive")
        for k in ("submit_url", "cfp_url", "source_url"):
            u = c.get(k)
            if u and not re.match(r"^https?://", str(u)):
                problems.append(f"{name}: {k} is not a URL: '{u}'")
        for h in c.get("history") or []:
            if not isinstance(h, dict) or not h.get("date") or not h.get("change"):
                problems.append(f"{name}: history entries need date and change")

    for path in sorted((DATA / "runs").glob("*.json")):
        load(path)

    for p in problems:
        print(p)
    print(f"Checked {len(series)} series and {n} call files: {len(problems)} problem(s).")
    return 1 if (problems and "--strict" in sys.argv) else 0


if __name__ == "__main__":
    sys.exit(main())
