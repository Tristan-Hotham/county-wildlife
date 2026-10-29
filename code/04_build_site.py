"""Fill code/page_template.html with numbers from data/results.json and data/page.json -> index.html."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

R = json.load(open(os.path.join(DATA, 'results.json')))
PG = json.load(open(os.path.join(DATA, 'page.json')))
S = R['signature']
M = R['meta']

def n0(x): return f"{round(x):,}"
def mil(x): return f"{x / 1e6:.1f}".rstrip('0').rstrip('.')
def lq(x): return f"{x:,.0f}" if x >= 10 else f"{x:.1f}"

V = {
    'records_m': mil(M['records_in_vcs']), 'records': n0(M['records_in_vcs']), 'records_open': n0(M['records_open']),
    'cc_by': n0(M['records_cc_by']), 'ogl': n0(M['records_ogl']), 'cc0': n0(M['records_cc0']),
    'counties': M['counties'], 'gb_vcs': M['gb_vcs'], 'ni_vcs': M['ni_vcs'], 'species': n0(M['species_in_vcs']), 'picker': n0(M['species_picker']),
    'min_sp_vc': M['min_sp_vc'], 'min_sp_uk': M['min_sp_uk'], 'min_group': n0(M['min_group_vc']), 'min_group_small': M['min_group_vc_small'], 'only_min': M['only_min'],
    'min_group_raw': M['min_group_vc'], 'ci': int(M['ci'] * 100), 'retrieved': '29 October 2026',
    'n_birds': R['signature_animal_by_group'].get('birds', 0), 'n_mammals': R['signature_animal_by_group'].get('mammals', 0),
    'n_butterflies': R['signature_animal_by_group'].get('butterflies', 0), 'n_dragonflies': R['signature_animal_by_group'].get('dragonflies', 0), 'n_herps': R['signature_animal_by_group'].get('herps', 0),
    'eff_max_name': R['effort']['most_per_km2'][0][0], 'eff_max': n0(R['effort']['most_per_km2'][0][1]), 'eff_min_name': R['effort']['least_per_km2'][0][0], 'eff_min': n0(R['effort']['least_per_km2'][0][1]),
    'eff_ratio': f"{R['effort']['ratio_max_min']:.0f}", 'eff_median': n0(R['effort']['median_per_km2']),
    'dist_top': R['distinct_animals'][0][0], 'dist_2': R['distinct_animals'][1][0], 'dist_3': R['distinct_animals'][2][0],
    'dist_low': R['distinct_animals'][-1][0], 'dist_low2': R['distinct_animals'][-2][0],
    'dist_eng': f"{R['distinct_nation_mean']['England']:.2f}", 'dist_sco': f"{R['distinct_nation_mean']['Scotland']:.2f}", 'dist_wal': f"{R['distinct_nation_mean']['Wales']:.2f}", 'dist_ni': f"{R['distinct_nation_mean']['Northern Ireland']:.2f}",
    'only_total': R['only_here']['total_species'], 'only_plants': R['only_here']['by_group'].get('plants', 0), 'only_moths': R['only_here']['by_group'].get('moths', 0),
    'only_top': R['only_here']['top_counties'][0][0], 'only_top_n': R['only_here']['top_counties'][0][1], 'only_top2': R['only_here']['top_counties'][1][0],
    'scotch_argus_n': dict(R['signature_animal_species_counts']).get('Scotch Argus', 0),
    'hooded_ni': sum(1 for k, v in S.items() if k in ('Fermanagh', 'Tyrone', 'Armagh', 'Down', 'Antrim', 'Londonderry') and v['birds'] and v['birds'][0] == 'Hooded Crow'),
}
for key, county, g in [('corn', 'Mid Ebudes', 'birds'), ('manx', 'Pembrokeshire', 'birds'), ('crest', 'Moray', 'birds'), ('swal', 'East Norfolk', 'butterflies'),
                       ('cheq', 'West Inverness-shire', 'butterflies'), ('ring', 'Mid Perthshire', 'butterflies'), ('glan', 'Isle of Wight', 'butterflies'), ('chough', 'Caernarvonshire', 'birds'),
                       ('cwd', 'Huntingdonshire', 'mammals'), ('cirl', 'South Devon', 'birds'), ('boar', 'West Gloucestershire', 'mammals'), ('stoat', 'Orkney', 'mammals'),
                       ('natter', 'West Norfolk', 'herps'), ('sand', 'Dorset', 'herps'), ('beaver', 'Mid Perthshire', 'mammals'), ('stone', 'South Wiltshire', 'birds'), ('skua', 'Shetland', 'birds'),
                       ('kentish', 'Moray', 'moths'), ('hood', 'Antrim', 'birds'), ('tenby', 'Pembrokeshire', 'plants')]:
    sp, l, n = S[county][g]
    V[key + '_sp'] = sp; V[key + '_lq'] = lq(l); V[key + '_n'] = n0(n); V[key + '_c'] = county
nc = {r['species']: r for r in R['newcomers']}
P = R['periods']
for key, sp in [('harl', 'Harlequin ladybird'), ('tree', 'Tree bumblebee'), ('para', 'Ring-necked parakeet'), ('egret', 'Little egret'), ('egy', 'Egyptian goose'), ('cetti', "Cetti's warbler"), ('sred', 'Small red-eyed damselfly')]:
    for k, pk in enumerate(P):
        V[f'{key}_{k}'] = nc[sp]['vc_' + pk]
V['DOI'] = DOI; V['PAGE'] = PAGE; V['REPO'] = REPO; V['BLOG'] = BLOG

t = open(os.path.join(os.path.dirname(__file__), 'page_template.html')).read()
def sub(m):
    k = m.group(1)
    if k not in V: raise KeyError(k)
    return str(V[k])
t = re.sub(r'\{\{(\w+)\}\}', sub, t)
t = t.replace('/*PAGE*/', json.dumps(PG, separators=(',', ':'), ensure_ascii=False))
open(os.path.join(ROOT, 'index.html'), 'w').write(t)
json.dump(V, open(os.path.join(ROOT, 'work', 'text_values.json'), 'w'), indent=0)
print('index.html', os.path.getsize(os.path.join(ROOT, 'index.html')))
