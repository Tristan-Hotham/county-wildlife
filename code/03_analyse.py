"""County wildlife: which species are over-represented in each vice county's records.

Input: the NBN Atlas facet bundle gathered in the browser (code/00_gather_browser.js), path in common.BUNDLE.
Outputs in data/: counties.csv, signature_species.csv, only_here.csv, newcomers.csv,
page.json and species_vc.json (for the interactive page), results.json (every number quoted anywhere).
"""
import json, gzip, csv, collections, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from scipy.stats import chi2
import numpy as np
NULL_DRAWS = 20

d = json.load(gzip.open(BUNDLE))
geo = json.load(open(os.path.join(DATA, 'vice_counties.geojson')))
SP = d['sp_list']                       # [lsid, scientific, vernacular, kingdom, family]
GKEYS = [g[0] for g in GROUPS]
ANIMALS = ['birds', 'mammals', 'herps', 'butterflies', 'dragonflies']

# ---- species groups --------------------------------------------------------------
lsid_group = {}
for l in d['groups']['FloweringPlants']: lsid_group[l] = 'plants'
fam = {s[0]: s[4] for s in SP}
for l in d['subgroups']['Butterflies and moths']: lsid_group[l] = 'butterflies' if fam.get(l) in BUTTERFLY_FAMILIES else 'moths'
for l in d['subgroups']['Dragonflies']: lsid_group[l] = 'dragonflies'
for g in ['Amphibians', 'Reptiles']:
    for l in d['groups'][g]: lsid_group[l] = 'herps'
for l in d['groups']['Mammals']: lsid_group[l] = 'mammals'
for l in d['groups']['Birds']: lsid_group[l] = 'birds'
EXCLUDE_WORDS = ('Domestic', 'domestic', 'Feral', 'Muscovy', 'Hybrid', 'hybrid', 'Human')
def excluded(s):
    return any(w in (s[2] or '') for w in EXCLUDE_WORDS) or s[1] in ('Homo sapiens', 'Bos taurus', 'Ovis aries', 'Capra hircus', 'Equus caballus', 'Felis catus', 'Canis familiaris', 'Sus scrofa domesticus', 'Cairina moschata', 'Columba livia', 'Anser cygnoides')
grp = [None if excluded(s) else lsid_group.get(s[0]) for s in SP]
nexcl = sum(1 for s in SP if excluded(s) and lsid_group.get(s[0]))
def vname(s):
    v = (s[2] or '').strip()
    return v if v else s[1]

# ---- counties --------------------------------------------------------------------
props = {}
for f in geo['features']:
    p = f['properties']
    n = p['num']
    if p['nation'] == '':
        p['nation'] = 'Isle of Man' if n == 71 else 'Scotland' if n >= 72 else 'Wales' if (n == 35 or 41 <= n <= 52) else 'England'
    props[p['name']] = p
VC = []
for k, v in d['vc'].items():
    if k == 'Not supplied': continue
    nm = k.split(' ', 1)[1] if k[:1] == 'H' and k[1:3].isdigit() else k
    VC.append((k, props[nm]))
VC.sort(key=lambda x: x[1]['num'])
cnt = {}
for k, p in VC:
    a = d['vc'][k]['sp']
    cnt[p['id']] = {a[i]: a[i + 1] for i in range(0, len(a), 2)}
ids = [p['id'] for _, p in VC]
P = {p['id']: p for _, p in VC}
RAW = {p['id']: d['vc'][k] for k, p in VC}

nat = collections.Counter()
for c in ids: nat.update(cnt[c])
NG = collections.Counter()
for i, n in nat.items(): NG[grp[i]] += n
GC = {c: collections.Counter() for c in ids}
SPC = {c: collections.Counter() for c in ids}
for c in ids:
    for i, n in cnt[c].items():
        GC[c][grp[i]] += n; SPC[c][grp[i]] += 1
nsp_g = collections.Counter(grp[i] for i in nat)

def lo(n):  # lower bound of a two-sided 90% Poisson interval
    return chi2.ppf((1 - CI) / 2, 2 * n) / 2 if n > 0 else 0.0
def min_group(g):
    return MIN_GROUP_VC_SMALL if g in SMALL_GROUPS else MIN_GROUP_VC

# ---- location quotients ----------------------------------------------------------
TOP = {}       # (c,g) -> list of dicts
for c in ids:
    for g in GKEYS:
        rows = []
        if GC[c][g] >= min_group(g):
            for i, n in cnt[c].items():
                if grp[i] != g or n < MIN_SP_VC or nat[i] < MIN_SP_UK: continue
                share_uk = nat[i] / NG[g]
                exp = GC[c][g] * share_uk
                rows.append(dict(i=i, n=n, exp=exp, lq=n / exp, lq_lo=lo(n) / exp))
        rows.sort(key=lambda r: -r['lq_lo'])
        TOP[(c, g)] = rows[:10]
def best_any(c, groups):
    cand = [(r, g) for g in groups for r in TOP[(c, g)][:1]]
    return max(cand, key=lambda x: x[0]['lq_lo']) if cand else (None, None)

# distinctiveness: half the sum of absolute differences between the county's species shares and the UK's
DIST = {}
for c in ids:
    for g in GKEYS:
        if GC[c][g] < min_group(g): continue
        tot = 0.0
        for i, n in nat.items():
            if grp[i] != g: continue
            tot += abs(cnt[c].get(i, 0) / GC[c][g] - n / NG[g])
        DIST[(c, g)] = tot / 2
# small samples look distinctive by chance: subtract the distance expected from a random sample of the same size
rng = np.random.default_rng(1)
NULL = {}
gidx = {g: [i for i in nat if grp[i] == g] for g in GKEYS}
gsh = {g: np.array([nat[i] for i in gidx[g]], float) / NG[g] for g in GKEYS}
for (c, g), v in DIST.items():
    draws = rng.multinomial(GC[c][g], gsh[g], size=NULL_DRAWS) / GC[c][g]
    NULL[(c, g)] = float(np.mean(np.abs(draws - gsh[g]).sum(axis=1) / 2))
XD = {k: DIST[k] - NULL[k] for k in DIST}

# only here
ONLY = collections.defaultdict(list)
where = collections.defaultdict(list)
for c in ids:
    for i, n in cnt[c].items(): where[i].append(c)
for i, cs in where.items():
    g = grp[i]
    if g and len(cs) == 1 and nat[i] >= ONLY_MIN:
        ONLY[cs[0]].append((g, i, nat[i]))

# ---- newcomers ---------------------------------------------------------------------
NEW = [  # scientific name as queried, label, status
    ('Harmonia axyridis', 'Harlequin ladybird', 'non-native'),
    ('Bombus hypnorum', 'Tree bumblebee', 'natural colonist'),
    ('Psittacula krameri', 'Ring-necked parakeet', 'non-native'),
    ('Alopochen aegyptiaca', 'Egyptian goose', 'non-native'),
    ('Egretta garzetta', 'Little egret', 'natural colonist'),
    ('Cettia cetti', "Cetti's warbler", 'natural colonist'),
    ('Erythromma viridulum', 'Small red-eyed damselfly', 'natural colonist'),
    ('Muntiacus reevesi', "Reeves' muntjac", 'non-native'),
    ('Sciurus carolinensis', 'Grey squirrel', 'non-native'),
    ('Sciurus vulgaris', 'Red squirrel', 'native'),
]
PERIODS = list(d['invasive']['Harmonia axyridis'].keys())
vcname = {}
for k, p in VC: vcname[k] = p['id']
newrows = []; newc = {}
for sci, lab, st in NEW:
    per = d['invasive'][sci]; row = {'species': lab, 'scientific': sci, 'status': st}
    byvc = {}
    for pk in PERIODS:
        q = per[pk]; pairs = [(vcname[a], b) for a, b in q['cl254'] + q['cl133'] if a in vcname]
        n2 = sum(1 for _, b in pairs if b >= 2)
        row['vc_' + pk] = n2; row['rec_' + pk] = q['total']
        for a, b in pairs:
            if b >= 2 and a not in byvc: byvc[a] = pk
    newrows.append(row); newc[sci] = byvc

# ---- outputs ----------------------------------------------------------------------
def r1(x): return round(x, 1)
def sprow(r, g):
    s = SP[r['i']]
    return dict(group=g, species=vname(s), scientific=s[1], n=r['n'], expected=round(r['exp'], 1), lq=r1(r['lq']), lq_lo=r1(r['lq_lo']), uk=nat[r['i']])

with open(os.path.join(DATA, 'counties.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['vc_id', 'vice_county', 'nation', 'area_km2', 'records', 'records_per_km2', 'datasets'] + [f'{g}_records' for g in GKEYS] + [f'{g}_species' for g in GKEYS] + ['signature_animal', 'signature_animal_group', 'signature_animal_lq', 'signature_animal_records'] + [f'signature_{g}' for g in GKEYS] + [f'signature_{g}_lq' for g in GKEYS] + [f'distinct_{g}' for g in GKEYS] + [f'distinct_excess_{g}' for g in GKEYS] + ['only_here_species'])
    for c in ids:
        p = P[c]; tot = sum(GC[c].values())
        ba, bg = best_any(c, ANIMALS)
        w.writerow([c, p['name'], p['nation'], p['area_km2'], RAW[c]['total'], round(RAW[c]['total'] / p['area_km2'], 1), RAW[c]['n_datasets']] + [GC[c][g] for g in GKEYS] + [SPC[c][g] for g in GKEYS]
                   + ([vname(SP[ba['i']]), bg, r1(ba['lq']), ba['n']] if ba else ['', '', '', ''])
                   + [vname(SP[TOP[(c, g)][0]['i']]) if TOP[(c, g)] else '' for g in GKEYS] + [r1(TOP[(c, g)][0]['lq']) if TOP[(c, g)] else '' for g in GKEYS]
                   + [round(DIST[(c, g)], 3) if (c, g) in DIST else '' for g in GKEYS] + [round(XD[(c, g)], 3) if (c, g) in XD else '' for g in GKEYS] + [len(ONLY[c])])
with open(os.path.join(DATA, 'signature_species.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, ['vc_id', 'vice_county', 'group', 'rank', 'species', 'scientific', 'n', 'expected', 'lq', 'lq_lo', 'uk'])
    w.writeheader()
    for c in ids:
        for g in GKEYS:
            for k, r in enumerate(TOP[(c, g)], 1):
                w.writerow(dict(vc_id=c, vice_county=P[c]['name'], rank=k, **sprow(r, g)))
with open(os.path.join(DATA, 'only_here.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['vc_id', 'vice_county', 'group', 'species', 'scientific', 'records'])
    for c in ids:
        for g, i, n in sorted(ONLY[c], key=lambda x: (x[0], -x[2])):
            w.writerow([c, P[c]['name'], g, vname(SP[i]), SP[i][1], n])
with open(os.path.join(DATA, 'newcomers.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, list(newrows[0].keys())); w.writeheader(); w.writerows(newrows)

# page data -------------------------------------------------------------------------
# species list for the picker: the seven groups, at least MIN_SP_UK records in all
pick = [i for i in nat if grp[i] and nat[i] >= MIN_SP_UK]
pick.sort(key=lambda i: (GKEYS.index(grp[i]), -nat[i]))
cidx = {c: k for k, c in enumerate(ids)}
spv = []
for i in pick:
    arr = []
    for c in ids:
        n = cnt[c].get(i, 0)
        if n: arr += [cidx[c], n]
    spv.append([vname(SP[i]), SP[i][1], GKEYS.index(grp[i]), nat[i], arr])
json.dump({'groups': GKEYS, 'species': spv}, open(os.path.join(DATA, 'species_vc.json'), 'w'), separators=(',', ':'), ensure_ascii=False)

page = {'groups': [[k, l, col, NG[k], nsp_g[k]] for k, l, col in GROUPS], 'counties': []}
for c in ids:
    p = P[c]; ba, bg = best_any(c, ANIMALS)
    e = {'id': c, 'name': p['name'], 'nation': p['nation'], 'area': p['area_km2'], 'rec': RAW[c]['total'], 'nds': RAW[c]['n_datasets'],
         'ds': [[a, b] for a, b in RAW[c]['top_datasets'][:3]], 'gc': [GC[c][g] for g in GKEYS], 'gs': [SPC[c][g] for g in GKEYS],
         'dist': [round(XD[(c, g)], 3) if (c, g) in XD else None for g in GKEYS], 'only': [], 'top': {}}
    for g in GKEYS:
        e['top'][g] = [[vname(SP[r['i']]), SP[r['i']][1], r['n'], r1(r['lq']), r1(r['lq_lo'])] for r in TOP[(c, g)][:5]]
    e['animal'] = [vname(SP[ba['i']]), SP[ba['i']][1], ba['n'], r1(ba['lq']), r1(ba['lq_lo']), bg] if ba else None
    for g, i, n in sorted(ONLY[c], key=lambda x: -x[2])[:8]:
        e['only'].append([vname(SP[i]), SP[i][1], GKEYS.index(g), n])
    e['n_only'] = len(ONLY[c])
    page['counties'].append(e)
page['newcomers'] = [[r['species'], r['scientific'], r['status'], [r['vc_' + pk] for pk in PERIODS], [cidx[c] * 10 + PERIODS.index(pk) for c, pk in newc[r['scientific']].items()]] for r in newrows]
page['periods'] = [pk.replace('-', ' to ') for pk in PERIODS]
json.dump(page, open(os.path.join(DATA, 'page.json'), 'w'), separators=(',', ':'), ensure_ascii=False)

# ---- results.json --------------------------------------------------------------
lic = dict(d['totals']['license'])
R = {'meta': {'retrieved': d['retrieved'][:10], 'counties': len(ids), 'gb_vcs': sum(1 for c in ids if c.startswith('VC')), 'ni_vcs': sum(1 for c in ids if c.startswith('H')),
              'records_open': d['totals']['records'], 'records_cc_by': lic.get('CC-BY'), 'records_ogl': lic.get('OGL'), 'records_cc0': lic.get('CC0'),
              'records_in_vcs': sum(nat.values()), 'species_in_vcs': len(nat), 'species_picker': len(pick), 'excluded_domestic_taxa': nexcl,
              'min_sp_vc': MIN_SP_VC, 'min_sp_uk': MIN_SP_UK, 'min_group_vc': MIN_GROUP_VC, 'min_group_vc_small': MIN_GROUP_VC_SMALL, 'ci': CI, 'only_min': ONLY_MIN, 'period_totals': d['period_totals']},
     'groups': {g: {'records': NG[g], 'species': nsp_g[g], 'counties_shown': sum(1 for c in ids if GC[c][g] >= min_group(g))} for g in GKEYS}}
recs = sorted(((RAW[c]['total'] / P[c]['area_km2'], c) for c in ids))
R['effort'] = {'most_per_km2': [[P[c]['name'], r1(v)] for v, c in recs[::-1][:5]], 'least_per_km2': [[P[c]['name'], r1(v)] for v, c in recs[:5]],
               'ratio_max_min': r1(recs[-1][0] / recs[0][0]), 'median_per_km2': r1(sorted(v for v, _ in recs)[len(recs) // 2])}
sig = {}
for c in ids:
    ba, bg = best_any(c, ANIMALS)
    sig[P[c]['name']] = {'animal': vname(SP[ba['i']]) if ba else None, 'group': bg, 'lq': r1(ba['lq']) if ba else None, 'n': ba['n'] if ba else None,
                         **{g: ([vname(SP[TOP[(c, g)][0]['i']]), r1(TOP[(c, g)][0]['lq']), TOP[(c, g)][0]['n']] if TOP[(c, g)] else None) for g in GKEYS}}
R['signature'] = sig
R['signature_animal_by_group'] = collections.Counter(v['group'] for v in sig.values() if v['group'])
R['signature_animal_species_counts'] = collections.Counter(v['animal'] for v in sig.values() if v['animal']).most_common(12)
R['distinct'] = {g: sorted([[P[c]['name'], round(XD[(c, g)], 3), round(DIST[(c, g)], 3)] for c in ids if (c, g) in DIST], key=lambda x: -x[1])[:5] for g in GKEYS}
R['distinct_least'] = {g: sorted([[P[c]['name'], round(XD[(c, g)], 3)] for c in ids if (c, g) in DIST], key=lambda x: x[1])[:3] for g in GKEYS}
R['only_here'] = {'total_species': sum(len(v) for v in ONLY.values()), 'by_group': collections.Counter(g for v in ONLY.values() for g, _, _ in v),
                  'top_counties': sorted([[P[c]['name'], len(ONLY[c])] for c in ids], key=lambda x: -x[1])[:8]}
am = {c: np.mean([XD[(c, g)] for g in ANIMALS if (c, g) in XD]) for c in ids}
R['distinct_animals'] = sorted([[P[c]['name'], round(float(v), 3)] for c, v in am.items()], key=lambda x: -x[1])
R['distinct_nation_mean'] = {n: round(float(np.mean([am[c] for c in ids if P[c]['nation'] == n])), 3) for n in sorted({P[c]['nation'] for c in ids})}
R['newcomers'] = newrows
R['periods'] = PERIODS
json.dump(R, open(os.path.join(DATA, 'results.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps({k: R[k] for k in ['meta', 'groups', 'effort', 'signature_animal_by_group', 'signature_animal_species_counts', 'distinct', 'only_here']}, indent=0)[:6000])
