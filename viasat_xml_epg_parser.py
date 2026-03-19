"""
EPG XML Parser — Viasat Press / Pawa.tv
========================================
Fetches a single EPG XML schedule file by URL, parses it,
and writes a structured JSON output file.

Output structure:
{
  "channel":  "Epic Drama (CEE)",
  "month":    "3",
  "year":     "2026",
  "source":   "https://...",
  "schedule": [
    {
      "date": "2026-03-01",
      "programs": [ { ...program fields... }, ... ]
    },
    ...
  ]
}

Usage:
    python parser.py <xml_url>
    python parser.py <xml_url> --output ./data
    python parser.py <xml_url> --output ./data --filename my_schedule.json

Examples:
    python parser.py "https://viasat-press.pawa.tv/Epic%20Drama%20(CEE)/English/2026-03-Epic%20Drama%20(CEE)-EET.xml"
    python parser.py "https://viasat-press.pawa.tv/Epic%20Drama%20(CEE)/English/2026-03-Epic%20Drama%20(CEE)-EET.xml" --output ./data
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote

import requests


# Config

DEFAULT_OUTPUT_DIR = "data"


# Helpers

def get_text(element, tag, default=None):
    """Return stripped text of a child tag or default if missing or empty."""
    node = element.find(tag)
    if node is None or node.text is None:
        return default
    text = node.text.strip()
    return text if text else default


def get_int(element, tag, default=None):
    """Return int value of a child tag or default."""
    val = get_text(element, tag)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default


def parse_bool(value):
    """Convert 'TRUE'/'FALSE' strings to bool."""
    if value is None:
        return None
    return value.strip().upper() == "TRUE"


def parse_cast(program_el):
    """Extract all cast members  as a list of members."""
    cast_node = program_el.find("cast")
    if cast_node is None:
        return []
    return [
        m.text.strip()
        for m in cast_node.findall("castMember")
        if m.text and m.text.strip()
    ]


def parse_directors(program_el):
    """Split comma-separated director string into a list."""
    raw = get_text(program_el, "director")
    if not raw:
        return []
    return [d.strip() for d in raw.split(",") if d.strip()]


def parse_countries(program_el):
    """Extract all country entries as a list."""
    node = program_el.find("countriesOfOrigin")
    if node is None:
        return []
    return [
        c.text.strip()
        for c in node.findall("country")
        if c.text and c.text.strip()
    ]


# ── Core parser ───────────────────────────────────────────────────────────────

def parse_program(program_el):
    """Parse a single <program> element into a dictionary."""
    return {
        "start_time":             get_text(program_el, "startTime"),
        "duration_minutes":       get_int(program_el, "duration"),
        "title_local":            get_text(program_el, "n"),
        "title_original":         get_text(program_el, "orgName"),
        "season":                 get_int(program_el, "season"),
        "episode":                get_int(program_el, "episode"),
        "episode_title_local":    get_text(program_el, "episodeTitle"),
        "episode_title_original": get_text(program_el, "originalEpisodeTitle"),
        "directors":              parse_directors(program_el),
        "cast":                   parse_cast(program_el),
        "category":               get_text(program_el, "programmeType"),
        "genre":                  get_text(program_el, "genre"),
        "parental_rating":        get_text(program_el, "parentalRating"),
        "production_countries":   parse_countries(program_el),
        "production_year":        get_int(program_el, "productionYear"),
        "live":                   parse_bool(get_text(program_el, "live")),
        "premiere":               parse_bool(get_text(program_el, "premiere")),
        "rerun":                  parse_bool(get_text(program_el, "rerun")),
        "high_definition":        parse_bool(get_text(program_el, "highDefinition")),
        "description_program":    get_text(program_el, "synopsis"),
        "description_episode":    get_text(program_el, "synopsisThisEpisode"),
    }


def parse_xml(xml_content, source_url=""):
    """
    Parse full XML content string into a structured dict.
    Returns None on parse failure.
    """
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as exc:
        print(f"[ERROR] XML parse failed: {exc}", file=sys.stderr)
        return None

    schedule = []
    for day_el in root.findall("day"):
        programs = [parse_program(p) for p in day_el.findall("program")]
        schedule.append({
            "date":     day_el.attrib.get("date", ""),
            "programs": programs,
        })

    return {
        "channel":  root.attrib.get("channel", ""),
        "month":    root.attrib.get("month", ""),
        "year":     root.attrib.get("year", ""),
        "source":   source_url,
        "schedule": schedule,
    }


# output helpers 

def safe_filename(text):
    """Replace characters that are unsafe in filenames."""
    for ch in r'<>:"/\\|?*() ':
        text = text.replace(ch, "_")
    return text.strip("_")


def build_output_path(url, output_dir, custom_filename=None):
    """
    Derive a clean output filename from the URL, e.g.:
      2026-03-Epic_Drama_CEE-EET.json
    """
    if custom_filename:
        filename = custom_filename
        if not filename.endswith(".json"):
            filename += ".json"
    else:
        basename = os.path.splitext(os.path.basename(unquote(url)))[0]
        filename = safe_filename(basename) + ".json"

    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, filename)


def main():
    parser = argparse.ArgumentParser(
        description="EPG XML parser — fetches a Viasat Press XML URL and outputs JSON."
    )
    parser.add_argument(
        "url",
        help="Full URL of the XML schedule file"
    )
    parser.add_argument(
        "--output", metavar="DIR", default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--filename", metavar="FILE",
        help="Custom output filename (default: derived from URL)"
    )
    args = parser.parse_args()

    # fetch XML
    print(f"Fetching: {args.url}")
    try:
        resp = requests.get(args.url, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8-sig"
        xml_text = resp.text
    except requests.RequestException as exc:
        print(f"[ERROR] Could not fetch URL: {exc}", file=sys.stderr)
        sys.exit(1)

    # Extract data
    print("Parsing XML...")
    result = parse_xml(xml_text, source_url=args.url)
    if result is None:
        sys.exit(1)

    # Save to JSON
    out_path = build_output_path(args.url, args.output, args.filename)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)

    program_count = sum(len(d["programs"]) for d in result["schedule"])
    print(f"Done. {len(result['schedule'])} days, {program_count} programs")
    print(f"Output: {out_path}")


if __name__ == "__main__":
    main()