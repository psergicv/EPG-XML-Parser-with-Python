# EPG XML Parser — Viasat Press / Pawa.tv

A scraper written in Pythin that fetches an EPG XML schedule file from the [Viasat Press](https://viasat-press.pawa.tv/) portal and converts it into clean, structured JSON.

---

## Features

- **Single URL input** — pass any XML schedule URL directly from the Viasat Press portal
- **Structured JSON output** — schedule split by date, each day containing its full program list
- **Clean field mapping** — all 20 EPG fields extracted with proper types
- **Robust parsing** — handles missing fields, empty tags, multi-value fields (cast, directors, countries)
- **Custom output** — configurable output directory and filename

---

## Output Structure

```json
{
  "channel": "Epic Drama (CEE)",
  "month": "3",
  "year": "2026",
  "source": "https://viasat-press.pawa.tv/...",
  "schedule": [
    {
      "date": "2026-03-01",
      "programs": [
        {
          "start_time": "06:10",
          "duration_minutes": 50,
          "title_local": "Miss Scarlet and The Duke",
          "title_original": "Miss Scarlet and The Duke",
          "season": 1,
          "episode": 5,
          "episode_title_local": "105",
          "episode_title_original": "105",
          "directors": ["Rachael New", "Declan O'Dwyer"],
          "cast": ["Kate Phillips", "Stuart Martin", "Cathy Belton"],
          "category": "Series",
          "genre": "Crime & Mystery",
          "parental_rating": null,
          "production_countries": ["United States"],
          "production_year": 2020,
          "live": false,
          "premiere": false,
          "rerun": true,
          "high_definition": true,
          "description_program": "The 1850s: Miss Scarlet runs her late father's detective agency...",
          "description_episode": "The final entry in her dad's casebook takes Eliza to a prison..."
        }
      ]
    }
  ]
}
```

---

## Installation

```bash
git clone https://github.com/psergicv/EPG-XML-Parser-with-Python.git
cd EPG XML Parser Project
pip install -r requirements.txt
```

**Requirements:** Python 3.8+

---

## Usage

### Basic
```bash
python viasat_xml_epg_parser.py "https://viasat-press.pawa.tv/Epic%20Drama%20(CEE)/English/2026-03-Epic%20Drama%20(CEE)-EET.xml"
```

### Custom output directory
```bash
python viasat_xml_epg_parser.py "<url>" --output ./data
```

### Custom output filename
```bash
python viasat_xml_epg_parser.py "<url>" --output ./data --filename epic_drama_march.json
```

XML URLs can be found on the [Viasat Press schedule page](https://viasat-press.pawa.tv/?language=All&timezone=All) — click the **XML Schedule** link for any channel.

---

## Extracted Fields

| Field | XML Source | Type |
|---|---|---|
| `start_time` | `<startTime>` | string |
| `duration_minutes` | `<duration>` | int |
| `title_local` | `<n>` | string |
| `title_original` | `<orgName>` | string |
| `season` | `<season>` | int |
| `episode` | `<episode>` | int |
| `episode_title_local` | `<episodeTitle>` | string |
| `episode_title_original` | `<originalEpisodeTitle>` | string |
| `directors` | `<director>` (split by comma) | list[str] |
| `cast` | `<cast><castMember>` | list[str] |
| `category` | `<programmeType>` | string |
| `genre` | `<genre>` | string |
| `parental_rating` | `<parentalRating>` | string \| null |
| `production_countries` | `<countriesOfOrigin><country>` | list[str] |
| `production_year` | `<productionYear>` | int |
| `live` | `<live>` | bool |
| `premiere` | `<premiere>` | bool |
| `rerun` | `<rerun>` | bool |
| `high_definition` | `<highDefinition>` | bool |
| `description_program` | `<synopsis>` | string |
| `description_episode` | `<synopsisThisEpisode>` | string |

---

## Tech Stack

- **Python 3.8+** — standard library only for XML parsing (`xml.etree.ElementTree`)
- **requests** — HTTP download

---

## Disclaimer

This tool is intended for educational and personal use.
All data belongs to Viasat / Pawa.tv. Please respect their terms of service.
