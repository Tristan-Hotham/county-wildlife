"""Place-name labels for the map: GeoNames cities1000 (CC BY 4.0), United Kingdom places
of 1,000 people or more. Output data/places.json as [name, lat, lon, rank] (rank 4 = largest).
Usage: python3 02_places.py <cities1000.zip> <out.json>"""
import sys, zipfile, json, io
z = zipfile.ZipFile(sys.argv[1]); out = []
with z.open('cities1000.txt') as f:
    for line in io.TextIOWrapper(f, encoding='utf-8'):
        c = line.rstrip('\n').split('\t')
        if c[8] != 'GB' or c[7].startswith('PPLX'):
            continue
        pop = int(c[14] or 0)
        if pop < 1000: continue
        r = 4 if pop >= 250000 else 3 if pop >= 60000 else 2 if pop >= 15000 else 1 if pop >= 4000 else 0
        out.append([c[1], round(float(c[4]), 4), round(float(c[5]), 4), r, pop])
out.sort(key=lambda p: -p[4])
json.dump([p[:4] for p in out], open(sys.argv[2], 'w'), separators=(',', ':'), ensure_ascii=False)
print(len(out), out[:5])
