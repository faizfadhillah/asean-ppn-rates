#!/usr/bin/env python3
"""
ASEAN PPN/VAT/GST Rate Checker

Fetches the latest VAT rates from PwC Tax Summaries and compares them
against our local dataset. If discrepancies are found, updates the JSON
and creates a summary for the commit message.

Usage:
  python3 scripts/check_rates.py          # check and report
  python3 scripts/check_rates.py --update # check and update JSON if changed
"""

import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "asean-ppn-rates.json"

# PwC Tax Summaries individual country pages (reliable, free, structured)
PWC_URLS = {
    "BN": "https://taxsummaries.pwc.com/brunei-darussalam/corporate/other-taxes",
    "KH": "https://taxsummaries.pwc.com/cambodia/corporate/other-taxes",
    "ID": "https://taxsummaries.pwc.com/indonesia/corporate/other-taxes",
    "LA": "https://taxsummaries.pwc.com/laos/corporate/other-taxes",
    "MY": "https://taxsummaries.pwc.com/malaysia/corporate/other-taxes",
    "MM": "https://taxsummaries.pwc.com/myanmar/corporate/other-taxes",
    "PH": "https://taxsummaries.pwc.com/philippines/corporate/other-taxes",
    "SG": "https://taxsummaries.pwc.com/singapore/corporate/other-taxes",
    "TH": "https://taxsummaries.pwc.com/thailand/corporate/other-taxes",
    "VN": "https://taxsummaries.pwc.com/vietnam/corporate/other-taxes",
}

# Known patterns to extract standard VAT/GST rate from PwC page text
RATE_PATTERNS = [
    r"(?:standard|general)\s+(?:VAT|GST|PPN|SST)\s+rate\s+(?:is|of)\s+(\d+(?:\.\d+)?)\s*%",
    r"VAT\s+(?:is\s+)?(?:levied|charged|imposed)\s+at\s+(?:a\s+)?(?:rate\s+of\s+)?(\d+(?:\.\d+)?)\s*%",
    r"(?:VAT|GST|PPN)\s+rate\s+(?:of|is)\s+(\d+(?:\.\d+)?)\s*%",
    r"(\d+(?:\.\d+)?)\s*%\s+(?:standard\s+)?(?:VAT|GST)",
    r"(?:service\s+tax)\s+(?:rate\s+)?(?:is|of|at)\s+(\d+(?:\.\d+)?)\s*%",
    r"commercial\s+tax\s+.*?(\d+(?:\.\d+)?)\s*%",
]


def load_local_rates() -> dict:
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_local_rates(data: dict) -> None:
    data["meta"]["last_updated"] = date.today().isoformat()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def fetch_page(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "ASEAN-PPN-Rates-Bot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ⚠ Failed to fetch {url}: {e}")
        return ""


def extract_rate(html: str, iso2: str) -> float | None:
    # Strip HTML tags for simpler regex matching
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    for pattern in RATE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))

    return None


def check_rates(update: bool = False) -> list[str]:
    data = load_local_rates()
    changes = []
    checked = 0

    print("🔍 Checking ASEAN PPN/VAT/GST rates against PwC Tax Summaries...\n")

    for entry in data["rates"]:
        iso2 = entry["iso2"]
        country = entry["country"]
        local_rate = entry["standard_rate"]
        url = PWC_URLS.get(iso2)

        if not url:
            print(f"  ⏭ {country} ({iso2}): no PwC URL configured")
            continue

        print(f"  📡 {country} ({iso2}): fetching...", end=" ")
        html = fetch_page(url)

        if not html:
            print("FAILED")
            continue

        remote_rate = extract_rate(html, iso2)
        checked += 1

        if remote_rate is None:
            print(f"local={local_rate}% | remote=PARSE_ERROR")
            continue

        if remote_rate != local_rate:
            change_msg = f"{country}: {local_rate}% → {remote_rate}%"
            changes.append(change_msg)
            print(f"⚠️ CHANGED! {local_rate}% → {remote_rate}%")
            if update:
                entry["standard_rate"] = remote_rate
                entry["effective_date"] = date.today().isoformat()
                entry["notes"] = f"Auto-updated from PwC on {date.today().isoformat()}. Previous rate: {local_rate}%. {entry.get('notes', '')}"
        else:
            print(f"✅ {local_rate}% (confirmed)")

    print(f"\n📊 Checked {checked}/{len(data['rates'])} countries")

    if changes:
        print(f"\n🔔 {len(changes)} rate change(s) detected:")
        for c in changes:
            print(f"   • {c}")
        if update:
            save_local_rates(data)
            print(f"\n💾 Updated {DATA_FILE}")
    else:
        print("\n✅ All rates match. No changes needed.")
        if update:
            # Still update the last_checked timestamp
            data["meta"]["last_updated"] = date.today().isoformat()
            save_local_rates(data)

    return changes


if __name__ == "__main__":
    update_mode = "--update" in sys.argv
    changes = check_rates(update=update_mode)
    sys.exit(1 if changes else 0)
