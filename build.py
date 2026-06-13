#!/usr/bin/env python3
"""Build runways.min.json from OurAirports runway data.

Produces an ICAO-keyed map of runway-end true headings, optimized for the
Groto-pilot dashboard's live crosswind calculation. The Infinity datasource
fetches this file and selects one airport's runways via root_selector.

Source: https://davidmegginson.github.io/ourairports-data/runways.csv
        (OurAirports data is public domain.)

Output shape (minified):
  {"KSFO": [{"id":"10L","hdg":118},{"id":"28R","hdg":298}, ...], ...}
  -> per airport, a list of runway ends with ident + true heading. Object
     form (not positional arrays) so Infinity parses named id/hdg fields.

Refresh roughly yearly (runway numbers drift with magnetic declination):
  python3 build.py && git commit -am "refresh runway data" && git push
"""

import csv
import json
import os
import urllib.request

SRC = "https://davidmegginson.github.io/ourairports-data/runways.csv"
CACHE = ".runways.csv.cache"
OUT = "runways.min.json"


def fetch():
    if os.path.exists(CACHE):
        return CACHE
    urllib.request.urlretrieve(SRC, CACHE)
    return CACHE


def build(path):
    out = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r["closed"] == "1":
                continue
            ident = r["airport_ident"].strip()
            # ICAO-style 4-char idents only: keeps the file small and matches
            # what the dashboard's airport dropdown can actually surface.
            if len(ident) != 4 or not ident.isalnum():
                continue
            ends = []
            for id_col, hdg_col in (("le_ident", "le_heading_degT"),
                                    ("he_ident", "he_heading_degT")):
                try:
                    hdg = round(float(r[hdg_col])) % 360
                except (ValueError, TypeError):
                    continue
                rid = r[id_col].strip()
                if rid:
                    ends.append({"id": rid, "hdg": hdg})
            if ends:
                out.setdefault(ident, []).extend(ends)
    return out


def main():
    data = build(fetch())
    with open(OUT, "w") as f:
        f.write(json.dumps(data, separators=(",", ":"), sort_keys=True))
    ends = sum(len(v) for v in data.values())
    size = os.path.getsize(OUT)
    print(f"{len(data)} airports, {ends} runway ends, {size/1024:.0f} KB -> {OUT}")


if __name__ == "__main__":
    main()
