# grotopilot-data

Static reference data for the [Groto-pilot](https://github.com/Praujekt) aviation
weather dashboard. Served via GitHub Pages so the dashboard's Infinity
datasource (which runs server-side in Grafana Cloud) can fetch it from a public
URL.

## runways.min.json

ICAO-keyed map of runway-end true headings, used to compute live crosswind for
any airport in the dashboard's dropdown.

```
{ "KSFO": [["10L",118],["28R",298], ...], ... }
```

Per airport: a list of `[runway_end_ident, true_heading_degrees]`. Headings are
true (not magnetic), matching coded METAR wind direction, so crosswind is a
direct `wind_speed * sin(wind_dir - heading)`.

- ~10.4k airports, ~27k runway ends, ~376 KB raw (~91 KB gzipped).
- ICAO-style 4-character idents only; closed runways and runways without a
  surveyed heading are dropped.

**Public URL:** `https://praujekt.github.io/grotopilot-data/runways.min.json`

Infinity selects one airport with `root_selector = ${airport:raw}`.

## Refreshing

Runway numbers drift with magnetic declination, so refresh roughly yearly:

```bash
rm -f .runways.csv.cache
python3 build.py
git commit -am "refresh runway data" && git push
```

## Source / license

Built from [OurAirports](https://ourairports.com/data/) `runways.csv`, which is
released into the public domain. This repository's derived data is likewise
public domain.
