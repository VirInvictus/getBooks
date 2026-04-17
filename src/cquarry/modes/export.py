from __future__ import annotations

import csv
import json
import os
import sys

from cquarry.db import CalibreDB
from cquarry.helpers import calibre_rating_to_stars


from typing import Optional

def run_export(db: CalibreDB, output: str, fmt: str = "json", *,
               show_custom: Optional[str] = None,
               quiet: bool = False) -> None:
    """Export full library to JSON, CSV, or AI-readable format."""
    books = db.get_all_books()
    out_path = os.path.abspath(output)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    custom_data = {}
    if show_custom:
        try:
            custom_data = db.load_custom_column(show_custom)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return

    if fmt == "json":
        export_data = []
        for b in books:
            stars = calibre_rating_to_stars(b['rating'])
            book_dict = {
                "id": b['id'],
                "title": b['title'],
                "authors": [a.strip() for a in b['authors'].split(',')] if b['authors'] else [],
                "author_sort": b['author_sort'],
                "tags": [t.strip() for t in b['tags'].split(',')] if b['tags'] else [],
                "series": b['series'],
                "series_index": b['series_index'],
                "formats": [f.strip() for f in b['formats'].split(',')] if b['formats'] else [],
                "rating": stars,
                "publisher": b['publisher'],
                "languages": [l.strip() for l in b['languages'].split(',')] if b['languages'] else [],
                "added": (b['timestamp'] or '')[:10],
                "has_cover": bool(b['has_cover']),
            }
            if show_custom:
                book_dict[show_custom] = custom_data.get(b['id'])
            export_data.append(book_dict)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    elif fmt == "csv":
        fieldnames = [
            "id", "title", "authors", "author_sort", "tags", "series",
            "series_index", "formats", "rating", "publisher", "languages",
            "added", "has_cover"
        ]
        if show_custom:
            fieldnames.append(show_custom)
        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for b in books:
                stars = calibre_rating_to_stars(b['rating'])
                row = {
                    "id": b['id'],
                    "title": b['title'],
                    "authors": b['authors'] or '',
                    "author_sort": b['author_sort'] or '',
                    "tags": b['tags'] or '',
                    "series": b['series'] or '',
                    "series_index": b['series_index'] if b['series_index'] is not None else '',
                    "formats": b['formats'] or '',
                    "rating": stars if stars is not None else '',
                    "publisher": b['publisher'] or '',
                    "languages": b['languages'] or '',
                    "added": (b['timestamp'] or '')[:10],
                    "has_cover": b['has_cover'],
                }
                if show_custom:
                    row[show_custom] = custom_data.get(b['id'], '')
                w.writerow(row)
    elif fmt == "ai":
        with open(out_path, 'w', encoding='utf-8') as f:
            for b in books:
                line = []
                if b['title']: line.append(b['title'])
                if b['author_sort']: line.append(f"by {b['author_sort']}")
                if b['series']:
                    idx = f" #{b['series_index']}" if b['series_index'] is not None else ""
                    line.append(f"({b['series']}{idx})")
                if b['tags']: line.append(f"[{b['tags']}]")
                stars = calibre_rating_to_stars(b['rating'])
                if stars is not None: line.append(f"{stars}/5")
                if show_custom:
                    val = custom_data.get(b['id'])
                    if val: line.append(f"<{show_custom}: {val}>")
                f.write(" ".join(line) + "\n")
    else:
        print(f"Unknown format: {fmt}. Use 'json', 'csv', or 'ai'.", file=sys.stderr)
        return

    if not quiet:
        print(f"Exported {len(books)} books to: {out_path}")


def run_search_export(db: CalibreDB, query: str, output: str, *,
                      show_custom: Optional[str] = None,
                      quiet: bool = False) -> None:
    """Evaluate a search query and export matching books to a text file."""
    try:
        matching_ids = db.search(query)
    except Exception as e:
        print(f"Error parsing search query: {e}", file=sys.stderr)
        return

    if not matching_ids:
        print(f"No books matched the query: '{query}'. File not created.", file=sys.stderr)
        return

    books = [b for b in db.get_all_books() if b['id'] in matching_ids]
    out_path = os.path.abspath(output)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    
    custom_data = {}
    if show_custom:
        try:
            custom_data = db.load_custom_column(show_custom)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"Search Query: {query}\n")
        f.write(f"Matches: {len(books)}\n")
        f.write("=" * 40 + "\n\n")
        for b in books:
            author = b['author_sort'] or 'Unknown'
            title = b['title'] or 'Untitled'
            custom_str = ""
            if show_custom:
                val = custom_data.get(b['id'])
                if val: custom_str = f" <{show_custom}: {val}>"
            f.write(f"  * {title} - {author}{custom_str}\n")

    if not quiet:
        print(f"Exported {len(books)} matches to: {out_path}")
