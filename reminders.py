"""Daily CFP reminders, sent as GitHub issues (GitHub emails them to the repository owner).

For every announced call it sends up to three notices:
  - "New call"     when the call first appears on the tracker,
  - "30 days left" when the deadline is 30 or fewer days away,
  - "3 days left"  when the deadline is 3 or fewer days away (and not past).
If a deadline changes, the countdown notices are re-armed for the new date. State lives in data/notified.json.
The first run records every call already on the tracker and posts one summary instead of a flood of notices.

Environment: GITHUB_TOKEN, GITHUB_REPOSITORY. Pass --dry-run to print notices without posting or saving.
"""
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CALLS = ROOT / "data" / "calls"
STATE = ROOT / "data" / "notified.json"
SITE = "https://mishalahmed.github.io/econ-cfp/"
LOCAL_TZ = timezone(timedelta(hours=3))  # the maintainer's time zone (UTC+3)
DRY = "--dry-run" in sys.argv


def fmt(d):
    return d.strftime("%a %d %b %Y").replace(" 0", " ")


def parse(s):
    try:
        return date.fromisoformat(s) if s else None
    except ValueError:
        return None


def describe(c, today):
    dl = parse(c.get("deadline"))
    lines = [f"**{c['name']}**", f"Organizer: {c.get('organizer') or 'not stated'}"]
    if dl:
        when = fmt(dl) + "".join(f" {x}" for x in (c.get("deadline_time"), c.get("deadline_tz")) if x)
        lines.append(f"Deadline: {when} ({(dl - today).days} days from today)")
    else:
        lines.append("Deadline: not stated")
    if c.get("deadline_note"):
        lines.append(f"Note: {c['deadline_note']}")
    start, end = parse(c.get("conf_start")), parse(c.get("conf_end"))
    dates = f"{fmt(start)} to {fmt(end)}" if start and end and end != start else (fmt(start) if start else "not stated")
    place = ", ".join(x for x in (c.get("city"), c.get("country")) if x) or "not stated"
    lines += [f"Conference: {dates}, {place}", f"Full paper required: {c.get('full_paper_required') or 'not stated'}",
              f"Membership: {c.get('membership_required') or 'not stated'}"]
    for label, key in (("Call for papers", "cfp_url"), ("Submit", "submit_url")):
        if c.get(key):
            lines.append(f"{label}: {c[key]}")
    lines.append(f"Dashboard: {SITE}")
    lines.append("\n_Always confirm details on the official call before submitting._")
    return "\n\n".join(lines)


def post_issue(title, body):
    if DRY:
        print(f"--- {title}\n{body}\n")
        return
    req = urllib.request.Request(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues",
        data=json.dumps({"title": title, "body": body}).encode(),
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req) as r:
        print(f"posted: {title} ({r.status})")


def main():
    today = datetime.now(LOCAL_TZ).date()
    first_run = not STATE.exists()
    state = {} if first_run else json.loads(STATE.read_text(encoding="utf-8"))
    calls = []
    for p in sorted(CALLS.glob("*.json")):
        try:
            c = json.loads(p.read_text(encoding="utf-8-sig"))
        except ValueError:
            continue
        if c.get("status") == "announced":
            calls.append(c)

    summary = []
    for c in calls:
        cid, dl = c["id"], parse(c.get("deadline"))
        days = (dl - today).days if dl else None
        s = state.setdefault(cid, {})
        if s.get("deadline") != c.get("deadline"):          # new record or changed deadline: re-arm countdowns
            if "deadline" in s and s.get("deadline") is not None and days is not None and days >= 0:
                post_issue(f"Deadline changed: {c['name']} — now {fmt(dl)}", describe(c, today))
            s.update({"deadline": c.get("deadline"), "d30": None, "d3": None})
        if not s.get("new"):
            s["new"] = today.isoformat()
            if first_run:
                if days is None or days >= 0:
                    summary.append((dl or date.max, c))
            elif days is None or days >= 0:
                post_issue(f"New call: {c['name']} — deadline {fmt(dl) if dl else 'not stated'}", describe(c, today))
            if days is not None and days <= 30:             # the first notice already shows how close it is
                s["d30"] = today.isoformat()
            if days is not None and days <= 3:
                s["d3"] = today.isoformat()
            continue
        if days is None or days < 0:
            continue
        if days <= 3 and not s.get("d3"):
            post_issue(f"3 days left: {c['name']} — deadline {fmt(dl)}", describe(c, today))
            s["d3"] = today.isoformat()
            s["d30"] = s.get("d30") or today.isoformat()
        elif days <= 30 and not s.get("d30"):
            post_issue(f"30 days left: {c['name']} — deadline {fmt(dl)}", describe(c, today))
            s["d30"] = today.isoformat()

    if first_run and summary:
        summary.sort(key=lambda x: x[0])
        rows = "\n".join(f"- **{fmt(d) if d != date.max else 'not stated'}** — {c['name']} ({(d - today).days} days)"
                         if d != date.max else f"- not stated — {c['name']}" for d, c in summary)
        post_issue(f"CFP reminders are on: {len(summary)} open calls",
                   "From now on you will get a notice when a new call appears, 30 days before its deadline and "
                   "3 days before it.\n\nCalls open today:\n\n" + rows + f"\n\nDashboard: {SITE}")

    if not DRY:
        STATE.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
