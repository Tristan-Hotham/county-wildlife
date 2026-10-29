# Signature species: what makes each county's wildlife special

An interactive map of the species each of the 118 vice counties of Britain, the Isle of Man and Northern Ireland records far more often than the country as a whole, from 60,917,118 openly licensed NBN Atlas records since 2000. Choose a group (birds, mammals, amphibians and reptiles, butterflies, moths, dragonflies, flowering plants), map how distinctive each county is, map any of 2,740 species, watch ten newcomers spread, or see recording effort. Tap a county for its ranked species, single-county species and largest datasets. A "Map layers" panel sets the base map, hills, place names, species labels, borders and colour strength.

**Interactive version:** https://maps.tristanhotham.com/county-wildlife/

**Paper and archived release:** https://doi.org/10.5281/zenodo.23761435

A data study by Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349).

## Headline results

- 60,917,118 open records (CC0, CC BY, OGL) of 36,799 species since 2000 fall in the 118 vice counties; CC BY NC records are excluded.
- Strongest signatures: mountain ringlet in Mid Perthshire (906 times its national share of butterfly records), chequered skipper in West Inverness-shire (346), corncrake in the Mid Ebudes (175), crested tit in Moray (146), Manx shearwater in Pembrokeshire (70), chough in Caernarvonshire (81).
- A bird is the signature animal of 45 counties, a mammal of 33, a butterfly of 26, a dragonfly of 8, an amphibian or reptile of 6. The Scotch argus leads 6 counties; the hooded crow is the signature bird of 6 of 6 Northern Irish vice counties.
- Most distinctive animal records (chance-corrected): Shetland, Orkney, Outer Hebrides; least: Derbyshire, South-west Yorkshire. Mean by nation: Scotland 0.44, Northern Ireland 0.36, Wales 0.28, England 0.23.
- Newcomers: harlequin ladybird in 72 vice counties in 2000 to 2009 and 91 since 2020; tree bumblebee 9 to 109; ring-necked parakeet 15 to 56.
- Recording effort: Middlesex has 889 open records per km², Tyrone 35 (25-fold).

Every number is in `data/results.json`, which the page, paper, blog and collage are built from.

## Method in brief

Location quotient LQ = (records of species in county / records of its group in county) / (records of species everywhere / records of group everywhere). Thresholds: at least 20 records in the county and 200 in all; a group is ranked in a county only with at least 1,000 records (150 for mammals, amphibians and reptiles, and dragonflies). Ranking uses the lower bound of a 90% Poisson interval for the county count; the plain LQ is shown. Distinctiveness is total variation distance from the national mix minus its expectation under multinomial sampling (20 draws). "Only here": at least 5 records, all in one county. Newcomers: vice counties with at least 2 records per period.

## Files

| Path | What it is |
|---|---|
| `index.html` | The interactive page (county data embedded). |
| `header.png` | Social card (1200 by 630). |
| `data/vice_counties.geojson` | Simplified vice county boundaries (WGS84) with id, name, nation, area, label point. |
| `data/counties.csv` | One row per vice county: records, effort, group totals and species counts, signature per group, distinctiveness. |
| `data/signature_species.csv` | Top 10 species per county and group with records, expected records, LQ and cautious LQ. |
| `data/only_here.csv` | Species with all their records in one county. |
| `data/newcomers.csv` | Vice counties and records by period for ten species. |
| `data/species_vc.json` | Records per county for 2,740 species (the page's species picker). |
| `data/page.json`, `data/places.json` | Page data; GeoNames place labels. |
| `data/results.json` | Every number used anywhere. |
| `code/` | Scripts, run in order (below). |
| `release/` | Paper PDF and LaTeX, blog post and figures, Zenodo files. |
| `reddit/` | Collage and post text. |

## How to rerun

1. `code/00_gather_browser.js`: run in a browser tab on https://records-ws.nbnatlas.org/ to save `cw_nbn_vc_2026.json.gz` (facet counts only, about 3 MB). Set `CW_BUNDLE` to its path.
2. `python3 code/01_boundaries.py <BRC MLWM shapefile> <Irish VC geojson> data/vice_counties.geojson`
3. `python3 code/02_places.py <GeoNames cities1000.zip> data/places.json`
4. `python3 code/03_analyse.py`, `04_build_site.py`, `05_figures.py`, `06_paper.py` (xelatex), `07_release.py`, then `reddit/collage.py`.

## Sources and licences

- Records: NBN Atlas (https://nbnatlas.org), occurrence web services, retrieved 29 October 2026. Only records under CC0, CC BY 4.0 and OGL v3 were counted. Thanks to all the schemes, societies, records centres and recorders who share their data.
- Vice counties: Biological Records Centre, https://github.com/BiologicalRecordsCentre/vice-counties (GPL 3.0); Irish vice counties, OpenStreetMap contributors via https://github.com/SK53/Irish-Vice-Counties (ODbL).
- Place names: GeoNames (CC BY 4.0). Map tiles © Esri. Leaflet (BSD 2-Clause).
- Licences for this repository: see LICENSE (code MIT; derived counts CC BY 4.0; boundaries under their source licences; text and figures CC BY 4.0).

## Limits

Records are sightings people chose to submit; quotients describe the mix of records, not populations. Targeted surveys, crowd-pulling rarities and escapes can inflate a species in one county. Coastal counties include inshore waters. CC BY NC data are excluded, so moths in particular are thin. Plant records are mostly grid-square occurrences from the BSBI Plant Atlas 2020.

## Citation

Hotham, T. (2026) Signature species: what makes each county's wildlife special? Location quotients from open biological records. Zenodo. https://doi.org/10.5281/zenodo.23761435

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
