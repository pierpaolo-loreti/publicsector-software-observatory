"""Collect repository URLs and original metadata from Developers Italia."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

API = "https://api.developers.italia.it/v1/software"


def collect(limit=None, include_inactive=False):
    entries, seen_pages, seen_ids = [], set(), set()
    url = API
    while url:
        if url in seen_pages:
            raise ValueError("Catalogue pagination repeated a page")
        if urlsplit(url).netloc != urlsplit(API).netloc or urlsplit(url).scheme != "https":
            raise ValueError("Unexpected pagination destination")
        seen_pages.add(url)
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "public-sector-code-observatory"})
        with urlopen(request, timeout=60) as response:
            page = json.load(response)
        for entry in page["data"]:
            if not include_inactive and not entry.get("active", False):
                continue
            if entry["id"] in seen_ids:
                continue
            seen_ids.add(entry["id"])
            entries.append({
                "id": entry["id"], "repository": entry["url"],
                "active": entry.get("active"),
                "publiccode_yml": entry.get("publiccodeYml"),
                "catalogue_updated_at": entry.get("updatedAt"),
                "catalogue_record": entry,
            })
            if limit is not None and len(entries) >= limit:
                return entries
        next_page = page.get("links", {}).get("next")
        url = urljoin(url, next_page) if next_page else None
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--include-inactive", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("catalogue.json"))
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    try:
        entries = collect(args.limit, args.include_inactive)
        result = {"source": API, "retrieved_at": datetime.now(timezone.utc).isoformat(),
                  "limit": args.limit, "include_inactive": args.include_inactive, "entries": entries}
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Collection failed: {error}\n")
    print(f"Saved {len(entries)} entries to {args.output}")


if __name__ == "__main__":
    main()
