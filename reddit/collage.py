"""r/dataisbeautiful collage: signature species of every vice county (2400 x 3000 px)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'code'))
from figlib import *
import matplotlib.patheffects as pe
BGc = '#F4F1E4'
halo = [pe.withStroke(linewidth=3.2, foreground=BGc)]
ANIM = ['birds', 'mammals', 'herps', 'butterflies', 'dragonflies']
S = R['signature']; M = R['meta']

OFF = {'VC88': (150, 15)}
def labels(ax, items, fs, box=(1.2, 1.3), maxn=40, subfs=None):
    placed = []
    for pri, cid, t, sub in sorted(items, key=lambda x: -x[0]):
        x0, y0 = PTS[cid]; dx, dy = OFF.get(cid, (0, 0)); x, y = x0 + dx, y0 + dy; w = len(t) * fs * box[0] * .62; h = fs * 2.6 * box[1]
        bx = (x - w / 2, y - h * .55, x + w / 2, y + h * .45)
        if any(bx[0] < o[2] and bx[2] > o[0] and bx[1] < o[3] and bx[3] > o[1] for o in placed): continue
        placed.append(bx)
        if dx or dy: ax.plot([x0, x], [y0, y], color=FG, lw=.8, zorder=4); ax.plot(x0, y0, 'o', ms=3, color=FG, zorder=4)
        ax.text(x, y + 2, t, ha='center', va='bottom', fontsize=fs, family=SER, weight='semibold', color=FG, path_effects=halo, zorder=5)
        if sub: ax.text(x, y, sub, ha='center', va='top', fontsize=subfs or fs * .8, family=MONO, color=FG, path_effects=halo, zorder=5)
        if len(placed) >= maxn: break

fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BGc)
fig.text(.04, .968, 'Every county has a signature species', fontproperties=DISP, fontsize=40, color=FG, va='top')
fig.text(.04, .925, f"The animal each vice county of Britain and Northern Ireland records far more often than the country as a whole,\nfrom {M['records_in_vcs'] / 1e6:.1f} million open wildlife records since 2000. Label: species and how many times its national share.",
         family=SER, fontsize=14.5, color=FG, va='top', linespacing=1.35)
ax = fig.add_axes([.0, .275, .6, .6])
draw_counties(ax, lambda c: sig_colour(c, 'animals', BGc), ec=BGc, lw=.7)
PREF = ['Mid Ebudes', 'Mid Perthshire', 'Pembrokeshire', 'Moray', 'Caernarvonshire', 'East Norfolk', 'South Devon', 'Argyll', 'Isle of Wight', 'Huntingdonshire', 'Shetland', 'Orkney']
items = [(c['animal'][3] + (1e5 - 1e3 * PREF.index(c['name']) if c['name'] in PREF else 0), c['id'], c['animal'][0], fq(c['animal'][3]) + '×') for c in PG['counties'] if c['animal']]
labels(ax, items, fs=9.5, box=(1.55, 1.75), maxn=36)
# right column
tx = fig.add_axes([.6, .44, .38, .42]); tx.axis('off')
notes = [(f"{fq(S['Mid Perthshire']['butterflies'][1])}×", f"Mountain ringlet in Mid Perthshire: its share of\nbutterfly records there against the UK. The\nstrongest signature on the map."),
         (f"{fq(S['Mid Ebudes']['birds'][1])}×", f"Corncrake in the Mid Ebudes (Mull, Coll, Tiree),\n{S['Mid Ebudes']['birds'][2]:,} records since 2000."),
         (f"{R['signature_animal_by_group']['birds']} of {M['counties']}", f"counties have a bird as their signature animal;\n{R['signature_animal_by_group']['mammals']} a mammal, {R['signature_animal_by_group']['butterflies']} a butterfly."),
         (f"{R['effort']['ratio_max_min']:.0f}×", f"more records per km² in {R['effort']['most_per_km2'][0][0]} than in\n{R['effort']['least_per_km2'][0][0]}. Shares, not counts, cancel that out.")]
for (big, small), y in zip(notes, [1.0, .75, .52, .29]):
    tx.text(0, y, big, fontproperties=DISP, fontsize=30, color=HOT, va='top', transform=tx.transAxes)
    tx.text(0, y - .085, small, family=SER, fontsize=12.5, color=FG, va='top', transform=tx.transAxes, linespacing=1.3)
lg = fig.add_axes([.6, .3, .38, .12]); lg.axis('off'); lg.set_xlim(0, 1); lg.set_ylim(0, 1)
for k, g in enumerate(ANIM):
    xx, yy = (k % 2) * .52, .85 - (k // 2) * .3
    lg.add_patch(plt.Rectangle((xx, yy - .1), .06, .2, color=GCOL[g]))
    lg.text(xx + .085, yy, {'herps': 'Amphibians', 'dragonflies': 'Dragonflies'}.get(g, GLAB[g]), va='center', family=MONO, fontsize=11.5, color=FG)
lg.text(.52, .25, 'Paler = weaker signal', va='center', family=MONO, fontsize=11, color=MUT)
# small multiples
SM = [('birds', 'BIRDS'), ('butterflies', 'BUTTERFLIES'), ('mammals', 'MAMMALS'), ('plants', 'FLOWERING PLANTS')]
for i, (g, lab) in enumerate(SM):
    a = fig.add_axes([.01 + i * .245, .085, .235, .165])
    draw_counties(a, lambda c, g=g: sig_colour(c, g, BGc), ec=BGc, lw=.3)
    top = sorted([(c['top'][g][0][3], c['id'], c['top'][g][0][0], '') for c in PG['counties'] if c['top'].get(g)], reverse=True)
    labels(a, top, fs=8.6, box=(4.2, 4.2), maxn=3)
    a.set_title(lab, family=MONO, fontsize=11.5, color=FG, pad=2, loc='left')
fig.text(.04, .27, 'EACH GROUP ON ITS OWN: SIGNATURE SPECIES, STRONGEST THREE LABELLED', family=MONO, fontsize=11, color=MUT)
fig.text(.04, .016, f"Data: NBN Atlas occurrence records since 2000 under CC0, CC BY and OGL only (CC BY NC excluded), counts by vice county, retrieved 29 Oct 2026.\nVice counties: Biological Records Centre (GPL 3.0), OpenStreetMap contributors (ODbL). Location quotient = species' share of its group's records in the\ncounty ÷ its share everywhere; at least 20 county records. Records reflect where people look as well as what lives there.\nAnalysis and chart: Tristan Hotham, with Python and matplotlib. maps.tristanhotham.com/county-wildlife",
         family=MONO, fontsize=9, color=MUT, linespacing=1.4)
fig.savefig(os.path.join(HERE, 'signature_species.png'), facecolor=BGc, dpi=200)
print('ok')
