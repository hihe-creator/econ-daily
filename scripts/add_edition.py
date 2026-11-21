#!/usr/bin/env python3
"""Merge one edition JSON file into data/editions.json.

Usage: python3 scripts/add_edition.py path/to/edition.json

- Replaces any existing edition with the same date.
- Keeps editions sorted newest first and at most MAX_EDITIONS of them.
- Validates the fields the page relies on and exits non-zero on problems.
"""
import json
import re
import sys
from pathlib import Path

MAX_EDITIONS = 400
CATS = {"통화정책", "금융시장", "외환", "무역·산업", "부동산", "글로벌", "정책·규제"}
FIG_TYPES = {"bars", "line", "range", "flow", "donut", "split", "stats", "compare"}
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "editions.json"


def validate(e):
    errs = []
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(e.get("date", ""))):
        errs.append("date must be YYYY-MM-DD")
    for k in ("headline", "lede"):
        if not isinstance(e.get(k), str) or not e[k].strip():
            errs.append(f"{k} is required")
    stories = e.get("stories")
    if not isinstance(stories, list) or not stories:
        errs.append("stories must be a non-empty list")
        stories = []
    for i, s in enumerate(stories):
        if s.get("cat") not in CATS:
            errs.append(f"stories[{i}].cat '{s.get('cat')}' not in {sorted(CATS)}")
        for k in ("title", "body"):
            if not isinstance(s.get(k), str) or not s[k].strip():
                errs.append(f"stories[{i}].{k} is required")
        for src in s.get("sources", []):
            if not str(src.get("url", "")).startswith(("http://", "https://")):
                errs.append(f"stories[{i}] source url must start with http(s)")
        figs = ([s["figure"]] if s.get("figure") else []) + list(s.get("figures") or [])
        for fig in figs:
            if fig.get("type") not in FIG_TYPES:
                errs.append(f"stories[{i}] figure type '{fig.get('type')}' must be one of {sorted(FIG_TYPES)}")
        for j, q in enumerate(s.get("quiz") or []):
            opts = q.get("options")
            if not isinstance(opts, list) or len(opts) < 2:
                errs.append(f"stories[{i}].quiz[{j}] needs at least 2 options")
            elif not isinstance(q.get("answer"), int) or not 0 <= q["answer"] < len(opts):
                errs.append(f"stories[{i}].quiz[{j}].answer must be a 0-based index into options")
            if not q.get("q") or not q.get("explain"):
                errs.append(f"stories[{i}].quiz[{j}] needs q and explain")
    for m in e.get("markets", []):
        if m.get("dir") not in (None, "up", "down", "flat"):
            errs.append(f"markets '{m.get('label')}' dir must be up/down/flat")
    return errs


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    new = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    errs = validate(new)
    if errs:
        sys.exit("Invalid edition:\n- " + "\n- ".join(errs))
    editions = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else []
    editions = [e for e in editions if e.get("date") != new["date"]]
    editions.append(new)
    editions.sort(key=lambda e: e["date"], reverse=True)
    editions = editions[:MAX_EDITIONS]
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(editions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {new['date']} written; {len(editions)} editions in {DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
