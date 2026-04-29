<p align="center">
  <img src="logo.svg" alt="CalibreQuarry" width="680">
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://ko-fi.com/vrnvctss"><img src="https://img.shields.io/badge/support-Ko--fi-ff5f5f?logo=kofi" alt="Ko-fi"></a>
</p>

A CLI toolkit for Calibre users who treat their libraries as curated collections. Reads `metadata.db` directly — no `calibredb` dependency, no JSON intermediaries, no external libraries. Pure Python stdlib.

> **Note:** This is considered completed software. It has been thoroughly tested and is known to be fully functional on the primary development environment: **Fedora Linux 43 (Workstation Edition)**, kernel `6.19.12-200.fc43.x86_64`, using **Calibre 9.7**. While it is pure Python and should be cross-platform, this specific setup is the only officially tested environment.

## Why this exists

Calibre is a good database. It is not a good reporting tool. If you maintain a large library (3000+ books) organized with virtual libraries, hierarchical tags, and series tracking, you eventually want answers to questions Calibre's UI doesn't surface well: which series have gaps, how many books are unrated, what does a given wing actually contain, and can I get a machine-readable export without running `calibredb list` through a parser script.

This tool reads the SQLite database directly in read-only mode. It resolves Calibre's virtual library search expressions (including `tags:`, `vl:` cross-references, and boolean operators), so your existing wing definitions work without being re-encoded anywhere.

## Features

| Mode | Flag | Description |
|------|------|-------------|
| **Catalog** | `--catalog` | Formatted text catalog grouped by author, with ratings and series info |
| **All wings** | `--all-wings` | Generate a separate catalog file for every virtual library |
| **Statistics** | `--stats` | Format breakdown, rating distribution, tag taxonomy, publisher counts |
| **Audit** | `--audit` | Report untagged, unrated, and coverless books; detect series gaps |
| **Recent** | `--recent N` | Show the N most recently added books (default: 20) |
| **Series** | `--series` | List all series with completeness status and gap detection |
| **Export** | `--export` | Full library export to JSON or CSV for external tools |
| **Wings** | `--wings` | List all virtual libraries with book counts |
| **Version** | `--version` | Show version and exit |

Modifiers: `--show-tags` swaps ratings for tag display in catalogs, `--show-id` prefixes each book with its Calibre ID (useful for scripting against `calibredb set_metadata`), `--primary-only` collapses multi-author entries to the first author, `--quiet` suppresses decorative output.

Running with no arguments launches a full-screen interactive TUI (arrow-key navigable) with a built-in scrollable output pager, or a text-based menu if `curses` is unavailable. The TUI remembers your database path between sessions.

## Installation

```bash
pip install .
# or
pipx install .
```

This gives you the `cquarry` command:

```bash
cquarry --catalog --db ~/Calibre/metadata.db
cquarry --stats
cquarry   # launches interactive TUI
```

Or run without installing:

```bash
PYTHONPATH=src python -m cquarry --stats
```

## Requirements

Python 3.9+. Zero external dependencies — uses only stdlib modules (`sqlite3`, `json`, `csv`, `argparse`, `curses`).

## Usage

```bash
# Build a catalog for a specific wing
cquarry --catalog --wing "The Tabletop" --primary-only --db ~/Calibre/metadata.db

# Same catalog, but showing tags instead of star ratings
cquarry --catalog --wing "The Tabletop" --show-tags --db ~/Calibre/metadata.db

# Catalog with Calibre IDs (for piping into calibredb set_metadata scripts)
cquarry --catalog --show-id --db ~/Calibre/metadata.db

# Generate catalogs for all virtual libraries at once
cquarry --all-wings --db ~/Calibre/metadata.db --outdir ~/docs/catalogs

# Library statistics
cquarry --stats --db ~/Calibre/metadata.db

# Audit: find unrated books, missing tags, series gaps
cquarry --audit --db ~/Calibre/metadata.db --output audit.csv

# Recently added books
cquarry --recent 10 --db ~/Calibre/metadata.db

# Series completeness and gap detection
cquarry --series --db ~/Calibre/metadata.db

# Export full library to JSON
cquarry --export --db ~/Calibre/metadata.db --format json --output library.json

# List all virtual library wings with counts
cquarry --wings --db ~/Calibre/metadata.db

# Check version
cquarry --version
```

If `metadata.db` is in the current directory or at `~/Calibre Library/metadata.db`, the `--db` flag can be omitted. On first run you'll be prompted for the path, which is saved to `~/.config/cquarry/config.json` for future sessions. If Calibre is running and has the database locked, CalibreQuarry will automatically read from a temporary snapshot.

## Sample output

### Catalog (`--catalog`)

```
Calibre Library Export — 2026-03-27 19:38 [The Tabletop]
========================================================

[Avery Alder]
-------------
  * The Quiet Year [PDF]

[Emmy Allen]
------------
  * The Gardens of Ynn [PDF]
  * The Stygian Library [PDF]

[Aaron Allston]
---------------
  * Dungeons and Dragons Rules Cyclopedia [PDF] [★★★★☆ 4.0/5]
```

### Statistics (`--stats`)

```
=== Library Statistics (3853 books) ===

Formats:
  EPUB    2571  ██████████████████████████
  PDF     1208  ████████████
  DJVU      65
  MOBI       8
  AZW3       3

Ratings:
  ★★★   (3.0)     81  █
  ★★★★  (4.0)   2031  ████████████████████████████████████████
  ★★★★★ (5.0)    135  ██
  Unrated:        1579  (41.0%)

Tag taxonomy (392 tags):
  NonFic: 276 tags
  Fic: 98 tags
  Gaming: 17 tags
```

### Series (`--series`)

```
  A Song of Ice and Fire: 5 of 5 (complete)
  Asian Saga: Chronological Order: 4 of 6 (incomplete)  ⚠ missing: 2, 3
  Aubrey-Maturin: 20 of 20 (complete)
  Discworld: 41 of 41 (complete)
  Parker: 10 of 18 (incomplete)  ⚠ missing: 8, 9, 10, 11, 12, 13, 14, 15
```

## Search Syntax & Virtual Library Resolution

CalibreQuarry features a pure-Python search expression parser that perfectly replicates Calibre's internal search rules. This engine is used both to resolve Virtual Libraries (Wings) directly from the `preferences` table, and for the `--search` CLI mode.

```
# Virtual Library Definitions
Fantasy Wing:    tags:"Fic.Fantasy" or tags:"Fic.Speculative.Fantasy"
The Tabletop:    tags:"Gaming.TTRPG"
Unsorted:        not (vl:"The Tabletop" or vl:"Fantasy Wing" or ...)

# CLI Search Queries
cquarry --search 'NOT(tags:Fic.Romance OR tags:Fic.Contemporary)'
cquarry --search 'tags:"Fic.Fantasy.Grimdark" AND author:"Phil Tucker"'
```

### Supported Search Features

* **Full Parity with Calibre:** The search engine has 100% parity with Calibre's internal search expression parser. It natively processes all standard operators, boolean groupings, quotes, and prefixes exactly as Calibre does.
* **General Text Search**: Just like Calibre, an un-prefixed term (e.g., `Rice`) acts as a wildcard search across book titles, authors, and tags.
* **Author Matching**: Use the `author:` or `authors:` prefixes to target authors.
* **Prefix & Exact Matching**: By default, Calibre searches are substring/hierarchical. Searching for `tags:Fic.Fantasy` will match `Fic.Fantasy`, `Fic.Fantasy.Epic`, `Fic.Fantasy.Grimdark`, and so on. To disable prefix matching and search for an exact string, prepend an equals sign: `tags:"=Fic.Fantasy"`.
* **Virtual Library Referencing**: You can use `vl:"Wing Name"` to cross-reference and search inside your existing Virtual Libraries.
* **Boolean Logic**: Fully supports `AND`, `OR`, and `NOT` operators. An implicit `AND` operation is performed when just separating terms with a space (e.g., `tags:Fic tags:SciFi` is the same as `tags:Fic AND tags:SciFi`).
* **Grouping**: Use parentheses `()` to enforce precedence in complex queries, such as `NOT(tags:Fic.Romance OR tags:Fic.Contemporary)` or `(tags:Fic OR tags:NonFic) AND NOT tags:Gaming`.

### Quote Handling (`"` and `'`)

When running searches via the command line with `--search`, you must navigate your shell's quote-escaping rules. Items can be explicitly `""`'d or written unquoted (if they do not contain spaces).

1. **Wrap the entire query in single quotes (`'`)**: This prevents your bash/zsh shell from trying to interpret spaces or special characters.
2. **Use double quotes (`"`) inside the query**: Use double quotes around tag names, author names, or virtual library names if they contain spaces.

**Good Examples:**
```bash
cquarry --search 'NOT(tags:Fic.Romance OR tags:Fic.Contemporary)'
cquarry --search 'tags:"Fic.Fantasy.Grimdark" AND author:"Phil Tucker"'
cquarry --search "author:Anne Rice"  # Handled natively as author:Anne AND Rice
```

**What to Avoid:**
* Unquoted spaces will break your shell command: `cquarry --search tags:Fic OR tags:SciFi` (Your shell thinks `OR` is a separate argument; instead use `--search 'tags:Fic OR tags:SciFi'`).
* Mismatched quotes will cause parsing errors: `cquarry --search "tags:'Fic.SciFi'"` (Calibre expects double quotes `"` internally, not single quotes).

### Automated Search Test Suite

CalibreQuarry includes an extensive automated test suite `tests/test_search.py` strictly designed to ensure zero drift from Calibre's native behavior. The suite verifies:
- Un-prefixed general term matching
- Implicit `AND` operations
- Exact string matching via `=` prefix
- Complex grouped boolean combinations and parenthetical negative lookaheads (`NOT(...)`)

## How it reads the database

CalibreQuarry opens `metadata.db` in read-only mode (`?mode=ro`). It never writes to the database. All data comes from standard Calibre tables: `books`, `authors`, `tags`, `series`, `ratings`, `data`, `publishers`, `languages`, and `preferences`. No custom columns are required.

If Calibre is running and holds a lock on the database, CalibreQuarry copies it (along with any WAL/SHM journal files) to a temporary snapshot and reads from that. A notice is printed to stderr; the temp files are cleaned up on exit.

Calibre stores ratings on a 0–10 scale internally (where 10 = 5 stars). CalibreQuarry converts to the standard 0-5 star display automatically.

## Replacing shell-based catalog pipelines

If you previously generated catalogs through a `calibredb list → JSON → parser` pipeline, `--all-wings` replaces that entire workflow with a single command. No temp files, no intermediate JSON, no shell glue functions.

The `--show-id` flag outputs Calibre book IDs, making it straightforward to pipe results into `calibredb set_metadata` for batch operations.

## Full help output

```
usage: cquarry [-h] [--version]
               [--catalog | --all-wings | --stats | --audit | --recent [RECENT]
               | --series | --export | --wings] [--db DB] [--wing WING]
               [--output OUTPUT] [--outdir OUTDIR] [--format {json,csv}]
               [--primary-only] [--show-tags] [--show-id] [--quiet]

Calibre library toolkit: catalog, stats, audit, export

options:
  -h, --help           show this help message and exit
  --version            show program's version number and exit
  --catalog            Build a text catalog
  --all-wings          Generate catalogs for all virtual libraries
  --stats              Show library statistics
  --audit              Report issues (untagged, unrated, series gaps)
  --recent [RECENT]    Show N most recently added books (default: 20)
  --series             List all series with completeness and gap detection
  --export             Export library to JSON or CSV
  --wings              List all virtual library wings
  --db DB              Path to Calibre metadata.db (auto-detected if omitted)
  --wing WING          Filter to a specific virtual library wing
  --output OUTPUT      Output file path
  --outdir OUTDIR      Output directory for --all-wings (default: current dir)
  --format {json,csv}  Export format (default: json)
  --primary-only       Use only the first author (useful for TTRPG
                       collections)
  --show-tags          Show tags instead of ratings in catalog output
  --show-id            Prefix each book with its Calibre ID for scripting
  --quiet              Minimize output
```

## Support

bc1qkge6zr45tzqfwfmvma2ylumt6mg7wlwmhr05yv
