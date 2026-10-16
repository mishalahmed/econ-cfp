# Econ CFP Dashboard: agent instructions

You maintain the data behind a public dashboard of **calls for papers (CFPs) for economics conferences**:
https://mishalahmed.github.io/econ-cfp/ (repository `mishalahmed/econ-cfp`). A GitHub Action rebuilds the site on
every push to `main` (`build_site.py` combines `data/` into `data.json`).

You only edit files under `data/`. Never edit `index.html`, `build_site.py`, `validate.py`, `AGENT.md` or the
workflow, unless the user asks you to.

```
data/sources.json          conference series to monitor ({"updated": ..., "series": [...]})
data/calls/<id>.json       one file per conference edition (announced call or expected call)
data/runs/<stamp>.json     one log file per run (stamp = YYYY-MM-DD_HHMM in UTC)
data/archive/              old call files moved here (never delete files)
```

---

## 1. Scope

The maintainer follows a **closed list of 32 conference series**: exactly the series in `data/sources.json`.
Do not add new series, and never re-add anything in `data/removed/series.json`. Each series has exactly one
category (use these exact labels in `fields`):

| Category | Series (series_id) |
|---|---|
| `General` | ASSA / AEA (`assa-aea`), Econometric Society North American Winter Meeting (`es-nawm`), North American Summer Meeting (`es-nasm`), European Winter Meeting (`es-ewm`), EEA-ESEM (`eea-esem`), Royal Economic Society (`res`), IEA World Congress (`iea-world-congress`), Southern (`sea`), Midwest (`mea`), Western (`weai-annual`), Canadian Economics Association (`cea`), ABFER (`abfer`) |
| `IO` | IIOC (`iioc`), EARIE (`earie`), CEPR-JIE Applied IO (`cepr-applied-io`), BSE Summer Forum Applied IO (`bsf-io`), MaCCI (`macci-annual`), ZEW ICT (`zew-ict`), TSE Digital Economics (`tse-digital`), APIOC (`apioc`) |
| `Labor & Education` | SOLE (`sole`), EALE (`eale`), AASLE (`aasle`), SOLE/EALE/AASLE World Labor Conference (`labor-world-conference`), TSE-CEPR Human Capital (`cepr-human-capital`), AEFP (`aefp`), IWAEE (`iwaee`), APPAM (`appam`) |
| `Others` | Urban Economics Association North American (`uea-north-america`) and European (`uea-europe`) meetings, AREUEA sessions at ASSA (`areuea-assa`), AEA CTREE (`ctree`) |

**Regions**, determined by the conference venue (use these exact labels):

| Label | Countries |
|---|---|
| `US` | United States |
| `Canada` | Canada |
| `Europe` | All of Europe incl. UK, Switzerland, Norway, Iceland |
| `Far East` | Japan, South Korea, Taiwan, Hong Kong, Singapore |
| `Rotating` | A rotating series whose next venue is not yet known, or an edition held anywhere else (e.g. Australia; name the country in `country`) |

Record every edition of the listed series, wherever it is held (a rotating series may meet outside these regions;
then use `Rotating` and name the country in `country`). Online-only editions
are recorded with `format: null` and a note.
---

## 2. Rules for facts

1. Record only what an official page states. Anything not stated is `null` (the dashboard shows "not stated").
   **Never** infer the deadline, venue or dates of an announced call from previous years.
2. Prefer the organizer's own site. `source_url` is the page where you actually saw the information.
3. Dates are ISO `YYYY-MM-DD`. Copy the deadline time and time zone as stated (`"23:59"`, `"CET"`, `"ET"`,
   `"AoE"`, `"GMT"`...). If only a month is given, leave the date `null` and put the text in the `*_note` field.
   If a call has closed but its deadline date was never stated, keep `deadline: null` and start `deadline_note`
   with `"Closed"` (the dashboard then files it under closed calls).
4. Fees: copy as stated, with currency and member/non-member/student variants. `registration_fee_usd` is an
   approximate USD number for the regular (non-student) non-member early fee, or the only fee listed.
5. `region` follows the venue's country. `country` uses plain English names (`USA`, `UK`, `South Korea`, `Hong Kong`, ...).
6. `expected_deadline` (for `expected` records only) is an **estimate**: the last edition's deadline shifted by
   one cycle (one year for annual series). It exists only so the dashboard can sort; say so in `expected_note`.
7. Some sites show a bot check or return 403 to automated tools (e.g. earie.org, cepr.org, iaes.org). Never try
   to get around a bot check or CAPTCHA. Use other official pages instead (host university's conference page,
   co-organizer, the association's news page) and list the blocked URL under `unreachable`.
8. The repository and site are **public**. Never write personal remarks about the maintainer into any file.

---

## 3. File formats

### 3a. Series (entries of `data/sources.json` → `"series"`)

```json
{
  "series_id": "example-assoc",
  "name": "Example Association Annual Meeting",
  "organizer": "Example Association of Economists (EAE)",
  "fields": ["Labor & Education"],
  "home_region": "Europe",
  "frequency": "Annual",
  "homepage": "https://www.example-assoc.org/",
  "cfp_page": "https://www.example-assoc.org/conference/",
  "has_permanent_site": true,
  "site_note": null,
  "typical_call_posted": "November",
  "typical_deadline": "mid-February",
  "typical_conference": "early June",
  "associated_journal": "Example Journal of Economics",
  "notes": null
}
```
(Illustrative values only.) `series_id` is stable kebab-case, e.g. `eea-esem`, `iioc`, `sole`, `eale`, `aefp`.
If the series has **no permanent website** (each edition is hosted on a different university page), set
`has_permanent_site: false`, `homepage: null`, and explain in `site_note` how to find each edition
(e.g. "Hosted by rotating universities; search 'APIOC 2027'").

### 3b. Call (one file per edition: `data/calls/<id>.json`)

`id` = `<series_id>-<year of the conference>` (add `-spring`/`-autumn` etc. if a series has two editions a year).
File name = `<id>.json`. All keys must be present (use `null` when unknown).

```json
{
  "id": "example-assoc-2027",
  "series_id": "example-assoc",
  "status": "announced",
  "name": "EAE 2027 Annual Meeting",
  "edition": "25th Annual Meeting",
  "organizer": "Example Association of Economists (EAE)",
  "fields": ["Labor & Education"],
  "region": "Europe",
  "city": "Lisbon",
  "country": "Portugal",
  "venue": "Nova School of Business and Economics",
  "conf_start": "2027-06-03",
  "conf_end": "2027-06-05",
  "conf_dates_note": null,
  "format": "In-person",
  "call_type": "Papers",
  "deadline": "2027-02-15",
  "deadline_time": "23:59",
  "deadline_tz": "CET",
  "deadline_note": null,
  "full_paper_required": "Yes",
  "submission_requirements": "Full paper in PDF via the online system; max. one submission per author",
  "submission_fee": "None",
  "registration_fee": "EUR 300 members / EUR 400 non-members / EUR 150 students",
  "registration_fee_usd": 470,
  "registration_deadline": "2027-04-30",
  "membership_required": "Presenters must be EAE members at registration",
  "notification_date": "Mid-March 2027",
  "keynotes": "Jane Doe (Univ. X); John Roe (Univ. Y)",
  "journal": "Selected papers invited to a fast-track at Example Journal of Economics",
  "submit_url": "https://www.example-assoc.org/submit",
  "cfp_url": "https://www.example-assoc.org/2027/call-for-papers",
  "contact": "conference@example-assoc.org",
  "source_url": "https://www.example-assoc.org/2027/call-for-papers",
  "first_seen": "2026-10-10",
  "last_verified": "2026-10-10",
  "updated_at": "2026-10-10",
  "change_kind": "new",
  "history": [{"date": "2026-10-10", "change": "Call announced"}],
  "expected_deadline": null,
  "expected_note": null,
  "last_edition": null
}
```
(Illustrative values only.)

Allowed values:
- `status`: `"announced"` (the call for this edition is published) or `"expected"` (series known, call not yet published)
- `format`: `"In-person"`, `"Hybrid"`, or `null`
- `call_type`: free text such as `"Papers"`, `"Papers and sessions"`, `"Session proposals"`, `"Abstracts"`
- `full_paper_required`: `"Yes"`, `"No (abstract)"`, `"Preferred"`, or `null`
- `change_kind`: `"seed"` (initial load), `"new"` (call newly published), `"changed"` (material change to a
  published call), `"expected"` (placeholder created). The dashboard flags only `new` and `changed`.
- `history`: list of `{"date", "change"}`, newest last. Describe changes concretely: `"Deadline extended: 2027-02-15 → 2027-03-01"`.

For an **expected** record, fill what is known about the coming edition (often only name/organizer/fields), set
`region` to the next venue's region if announced, else the series' home region (or `"Rotating"`), and fill:
```json
"expected_deadline": "2027-02-15",
"expected_note": "Call usually posted in November. Estimated from last edition's deadline (15 Feb 2026).",
"last_edition": {"year": 2026, "deadline": "2026-02-15", "conf_start": "2026-06-04", "conf_end": "2026-06-06",
                 "city": "Ghent", "country": "Belgium", "cfp_url": "https://..."}
```

### 3c. Run log (`data/runs/<YYYY-MM-DD_HHMM>.json`, UTC)

```json
{
  "started": "2026-10-12T06:04:00Z",
  "finished": "2026-10-12T06:41:00Z",
  "status": "complete",
  "trigger": "scheduled",
  "scope": "weekly",
  "sources_checked": 142,
  "new": [{"id": "eea-esem-2027", "name": "EEA-ESEM 2027", "deadline": "2027-02-15"}],
  "changed": [{"id": "sole-2027", "name": "SOLE 2027", "change": "Deadline extended: 2026-12-01 → 2026-12-08"}],
  "expected_added": ["sea-2027"],
  "series_added": ["new-series-id"],
  "archived": ["old-call-id"],
  "unreachable": [{"series_id": "xyz", "url": "https://...", "error": "HTTP 503"}],
  "notes": null
}
```
`status` is `"complete"` or `"partial"`. `trigger` is `"scheduled"`, `"manual"` or `"seed"`. `scope` is
`"weekly"`.

---

## 4. Weekly procedure

0. **Duplicate-run guard.** List `data/runs/`. If a run with `"status": "complete"` and a trigger other than
   `"seed"` finished less than 20 hours ago and your prompt does not say `force`, change nothing; reply
   `Already checked on <date>; nothing to do.` and stop.
1. **Load** `data/sources.json` and every file in `data/calls/`.
2. **Check every series every week** (there are only 32). Set the run log `scope` to `"weekly"`.
3. **Check each series.** Use the official `cfp_page` first, then `homepage`, then a web search for the
   current edition if the series has no permanent site. To keep this fast, split the series into batches of
   about 8 and give each batch to a parallel subagent. Each subagent edits only the call files of its own
   series, follows sections 2–3 exactly, and returns a list of new / changed / expected-added / unreachable
   items. For each series:
   - **Expected → announced:** if the call for an `expected` record is now published, fill every field, set
     `status: "announced"`, `change_kind: "new"`, `updated_at` = today, append history `"Call announced"`.
   - **Open call (deadline ≥ today):** re-verify deadline, dates, venue, format, requirements, fees and links.
     If a material field changed, update it, set `change_kind: "changed"`, `updated_at` = today and append a
     concrete history entry. Set `last_verified` = today whenever you confirmed the record.
   - **Closed call (deadline passed):** leave the record; make sure an `expected` record exists for the next
     edition (`change_kind: "expected"`).
   - **Page unreachable:** retry once; then record it under `unreachable` and leave the record unchanged.
4. **Archive:** move every call file whose conference ended more than 60 days ago to `data/archive/`
   (`git mv`; do not delete).
5. **No discovery.** Do not add series or call files for conferences outside the list. If you happen to see an
   important new call in IO, labor or education, mention it in the run log `notes` only.
6. **Validate:** run `python3 validate.py`. It checks every call file, `sources.json` and the run logs against
   this document and prints one line per problem. Fix every problem you caused and re-run until it reports 0
   (or only problems you cannot fix, which you then mention in the run log `notes`).
7. **Write the run log** (section 3c), even if nothing changed, and even if the run is partial.
8. **Commit and push to `main`:** `git add -A data && git commit -m "Weekly CFP check <YYYY-MM-DD>" && git push origin HEAD:main`.
   If the push is rejected because `main` moved, `git pull --rebase origin main` and push again. If pushing to
   `main` is not permitted, push a branch and say so in the final reply.
9. **Final reply.** First line exactly one of:
   - `🔔 N new call(s), M change(s): <short list> — https://mishalahmed.github.io/econ-cfp/`
   - `No new calls this week (<K> sources checked). https://mishalahmed.github.io/econ-cfp/`

   Then a short bullet list: each new or changed call with its deadline, any unreachable sources, and whether
   the push succeeded. Do not send emails, push or phone notifications, or post anywhere. Do not use social media.
