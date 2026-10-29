"""Build simplified vice-county boundaries (GB Watsonian VCs 1 to 112 plus the six
Northern Ireland vice counties H33, H36 to H40) as one small WGS84 GeoJSON.

Inputs (not kept in the repo, too big):
  GB: github.com/BiologicalRecordsCentre/vice-counties, MLWM/County_Coastal_Terrestrial_region.shp (GPL-3.0)
  NI: github.com/SK53/Irish-Vice-Counties, vice_counties/All_Irish_Vice_Counties_wgs84.geojson (ODbL, OpenStreetMap contributors)
Usage: python3 01_boundaries.py <gb_shp_without_ext> <ni_geojson> <out.geojson>
"""
import sys, json, shapefile
from shapely.geometry import shape, mapping, MultiPolygon, Polygon
from shapely.ops import transform
from pyproj import Transformer

gb_shp, ni_gj, out = sys.argv[1:4]
to_wgs = Transformer.from_crs(27700, 4326, always_xy=True).transform
ie_to_bng = Transformer.from_crs(4326, 27700, always_xy=True).transform

def clean(g, tol=500, minarea=400_000):
    g = g.buffer(0)
    polys = list(g.geoms) if isinstance(g, MultiPolygon) else [g]
    polys = [p for p in polys if p.area >= minarea] or [max(polys, key=lambda p: p.area)]
    g = MultiPolygon(polys).simplify(tol, preserve_topology=True)
    return g

def rnd(geom):
    def r(c):
        return [[round(x, 4), round(y, 4)] for x, y in c]
    m = mapping(geom)
    if m['type'] == 'Polygon':
        m['coordinates'] = [r(ring) for ring in m['coordinates']]
    else:
        m['coordinates'] = [[r(ring) for ring in poly] for poly in m['coordinates']]
    return m

feats = []
rd = shapefile.Reader(gb_shp)
for sr in rd.iterShapeRecords():
    num, name = int(sr.record[0]), sr.record[1]
    g = clean(shape(sr.shape.__geo_interface__))
    c = g.representative_point()
    gw = transform(to_wgs, g)
    cw = transform(to_wgs, c)
    feats.append({'type': 'Feature', 'properties': {'id': f'VC{num}', 'num': num, 'name': name, 'nation': '', 'area_km2': round(g.area / 1e6, 1), 'lon': round(cw.x, 4), 'lat': round(cw.y, 4)}, 'geometry': rnd(gw)})
ni = json.load(open(ni_gj))
for f in ni['features']:
    ref = f['properties']['ref']
    name = f['properties']['name'].split(' ', 1)[1]
    g = clean(transform(ie_to_bng, shape(f['geometry'])))
    c = g.representative_point()
    feats.append({'type': 'Feature', 'properties': {'id': ref, 'num': 200 + int(ref[1:]), 'name': name, 'nation': 'Northern Ireland', 'area_km2': round(g.area / 1e6, 1), 'lon': round(transform(to_wgs, c).x, 4), 'lat': round(transform(to_wgs, c).y, 4)}, 'geometry': rnd(transform(to_wgs, g))})
feats.sort(key=lambda f: f['properties']['num'])
json.dump({'type': 'FeatureCollection', 'features': feats}, open(out, 'w'), separators=(',', ':'))
print(len(feats), 'features')
