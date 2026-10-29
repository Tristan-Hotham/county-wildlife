"""Header card, blog figures (release/blog/b_*.png) and paper figures (release/paper/fig_*.png)."""
import os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *
import matplotlib.patheffects as pe
BLOG = os.path.join(ROOT, "release", "blog"); PAP = os.path.join(ROOT, "release", "paper")
halo = [pe.withStroke(linewidth=3, foreground=BG)]
ANIM = ["birds", "mammals", "herps", "butterflies", "dragonflies"]

def label_map(ax, items, fs=9.5, box=(1.0, 1.0), maxn=40):
    """items: (priority, cid, text, sub). Greedy non-overlapping labels in km space."""
    placed = []
    for pri, cid, t, sub in sorted(items, key=lambda x: -x[0]):
        x, y = PTS[cid]; w = len(t) * fs * box[0] * .62; h = fs * 2.6 * box[1]
        bx = (x - w / 2, y - h * .55, x + w / 2, y + h * .45)
        if any(bx[0] < o[2] and bx[2] > o[0] and bx[1] < o[3] and bx[3] > o[1] for o in placed): continue
        placed.append(bx)
        ax.text(x, y + 2, t, ha="center", va="bottom", fontsize=fs, family=SER, weight="semibold", color=FG, path_effects=halo, zorder=5)
        ax.text(x, y, sub, ha="center", va="top", fontsize=fs * .78, family=MONO, color=FG, path_effects=halo, zorder=5)
        if len(placed) >= maxn: break

def sig_map(path, w_in=7.6, h_in=11.2, fs=8.6, maxn=46, legend=True):
    fig = plt.figure(figsize=(w_in, h_in)); ax = fig.add_axes([0, 0, 1, 1])
    draw_counties(ax, sig_colour, ec="#FFFFFF", lw=.6)
    items = [(c["animal"][3], c["id"], c["animal"][0], fq(c["animal"][3]) + "×") for c in PG["counties"] if c["animal"]]
    label_map(ax, items, fs=fs, box=(1.2, 1.3), maxn=maxn)
    if legend:
        for k, g in enumerate(ANIM):
            ax.add_patch(plt.Rectangle((0, 420 - k * 30), 18, 18, color=GCOL[g], zorder=6))
            ax.text(26, 429 - k * 30, {"herps": "Amphibians, reptiles", "dragonflies": "Dragonflies"}.get(g, GLAB[g]), va="center", fontsize=10.5, family=MONO, color=FG)
        ax.text(0, 420 - 5 * 30 + 8, "Paler: weaker signal", fontsize=9.5, family=MONO, color=MUT, va="center")
    save(fig, path)

# 1. signature map
sig_map(os.path.join(BLOG, "b_signature_map.png"))

# 2. strongest signatures (lollipop, log scale)
rows = sorted([(c["animal"][3], c["animal"][0], c["name"], c["animal"][5]) for c in PG["counties"] if c["animal"]], reverse=True)[:16]
fig, ax = plt.subplots(figsize=(7.6, 6.4)); fig.subplots_adjust(left=.47, right=.95, top=.98, bottom=.1)
for k, (lq, sp, cn, g) in enumerate(rows):
    y = len(rows) - k
    ax.plot([1, lq], [y, y], color=GCOL[g], lw=2.2); ax.plot(lq, y, "o", color=GCOL[g], ms=8)
    ax.text(lq * 1.12, y, fq(lq) + "×", va="center", fontsize=10, family=MONO, color=FG)
    ax.text(.5, y, f"{sp}, ", ha="right", va="center", fontsize=11.5, color=FG, transform=ax.get_yaxis_transform(), weight="semibold")
ax.set_yticks(range(1, len(rows) + 1)); ax.set_yticklabels([r[2] for r in rows[::-1]], fontsize=10.5, family=MONO, color=MUT)
ax.set_yticklabels([]); 
for k, (lq, sp, cn, g) in enumerate(rows):
    ax.text(-0.02, len(rows) - k, f"{sp}", transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=11.5, weight="semibold", color=FG)
    ax.text(-0.02, len(rows) - k, f"{cn}", transform=ax.get_yaxis_transform(), ha="right", va="top", fontsize=9.5, family=MONO, color=MUT)
ax.set_xscale("log"); ax.set_xlim(1, 2500); ax.set_xticks([1, 10, 100, 1000]); ax.set_xticklabels(["1×", "10×", "100×", "1,000×"], family=MONO)
ax.set_xlabel("location quotient (log scale)", fontsize=10.5, family=MONO, color=MUT)
ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
for t in ax.texts:
    if t.get_text().endswith(", "): t.remove()
save(fig, os.path.join(BLOG, "b_strongest.png"))

# 3. distinctiveness map (animals)
dv = {}
for c in PG["counties"]:
    v = [c["dist"][GROUPS.index(next(x for x in GROUPS if x[0] == g))] for g in ANIM]
    v = [x for x in v if x is not None]; dv[c["id"]] = sum(v) / len(v) if v else None
RAMP = ["#F1EFD9", "#B9D3A0", "#5E9E5E", "#245A3A", "#0E2E22"]
def ramp(t):
    t = max(0, min(1, t)) * (len(RAMP) - 1); i = min(len(RAMP) - 2, int(t)); return mix(RAMP[i], RAMP[i + 1], t - i)
fig = plt.figure(figsize=(7.6, 10.6)); ax = fig.add_axes([0, 0, 1, 1])
draw_counties(ax, lambda cid: ramp((dv[cid] - .1) / .55) if dv[cid] is not None else FEW, lw=.6)
top = sorted(dv.items(), key=lambda x: -x[1])
lab = [(v, cid, CB[cid]["name"], f"{v:.2f}") for cid, v in top[:6]] + [(1 - v, cid, CB[cid]["name"], f"{v:.2f}") for cid, v in top[-5:]]
label_map(ax, lab, fs=9.5, box=(1.1, 1.0))
cax = fig.add_axes([.04, .3, .3, .018])
cax.imshow(np.array([[ramp(t) for t in np.linspace(0, 1, 100)]]), aspect="auto", extent=[.1, .65, 0, 1]); cax.set_yticks([]); cax.set_xticks([.1, .3, .5, .65]); cax.set_xticklabels(["0.1", "0.3", "0.5", "0.65"], family=MONO, fontsize=9)
for s in cax.spines.values(): s.set_visible(False)
fig.text(.04, .335, "Distance from the national mix,\nbeyond chance (animals)", family=MONO, fontsize=9.5, color=FG)
save(fig, os.path.join(BLOG, "b_distinct_map.png"))

# 4. newcomers small multiples
NC = R["newcomers"]; PER = R["periods"]
fig, axs = plt.subplots(2, 5, figsize=(7.6, 4.4), sharey=True); fig.subplots_adjust(left=.07, right=.99, top=.9, bottom=.1, wspace=.15, hspace=.62)
NCR = ["#2B1B4A", "#6B2E78", "#B4497A", "#E58466", "#F6D28B"]
for a, r in zip(axs.flat, NC):
    v = [r["vc_" + p] for p in PER]
    a.bar(range(5), v, color=NCR, width=.82)
    a.set_title(r["species"].replace("Small red-eyed damselfly", "Small red-eyed\ndamselfly").replace("Ring-necked parakeet", "Ring-necked\nparakeet").replace("Harlequin ladybird", "Harlequin\nladybird").replace("Tree bumblebee", "Tree\nbumblebee"), fontsize=9.5, family=SER, weight="semibold", loc="left", color=FG)
    a.set_xticks([0, 4]); a.set_xticklabels(["1970s", "2020s"], fontsize=8, family=MONO); a.set_ylim(0, 118)
    a.text(4, v[-1] + 3, str(v[-1]), ha="center", fontsize=8.5, family=MONO, color=FG)
    a.tick_params(axis="y", labelsize=8)
for a in axs[:, 0]: a.set_ylabel("vice counties", fontsize=9, family=MONO, color=MUT)
save(fig, os.path.join(BLOG, "b_newcomers.png"))

# 5. effort map
eff = {c["id"]: c["rec"] / c["area"] for c in PG["counties"]}
ER = ["#F0EEE6", "#C9D6DE", "#86A7BD", "#3F6E8F", "#16364F"]
def eramp(t):
    t = max(0, min(1, t)) * (len(ER) - 1); i = min(len(ER) - 2, int(t)); return mix(ER[i], ER[i + 1], t - i)
fig = plt.figure(figsize=(7.6, 10.6)); ax = fig.add_axes([0, 0, 1, 1])
draw_counties(ax, lambda cid: eramp((np.log10(eff[cid]) - 1.4) / 1.6), lw=.6)
es = sorted(eff.items(), key=lambda x: -x[1])
label_map(ax, [(v, cid, CB[cid]["name"], f"{v:,.0f} per km²") for cid, v in es[:2]] + [(1000 - v, cid, CB[cid]["name"], f"{v:,.0f} per km²") for cid, v in es[-4:]], fs=9.5, box=(1.15, 1.0))
cax = fig.add_axes([.04, .3, .3, .018])
cax.imshow(np.array([[eramp(t) for t in np.linspace(0, 1, 100)]]), aspect="auto", extent=[1.4, 3.0, 0, 1]); cax.set_yticks([]); cax.set_xticks([np.log10(30), 2, np.log10(300), 3]); cax.set_xticklabels(["30", "100", "300", "1,000"], family=MONO, fontsize=9)
for s in cax.spines.values(): s.set_visible(False)
fig.text(.04, .335, "Open records per km²\nsince 2000", family=MONO, fontsize=9.5, color=FG)
save(fig, os.path.join(BLOG, "b_effort_map.png"))

# 6. group counts bar
cnt = R["signature_animal_by_group"]
fig, ax = plt.subplots(figsize=(7.6, 3.0)); fig.subplots_adjust(left=.36, right=.95, top=.95, bottom=.12)
rows = sorted(ANIM, key=lambda g: cnt.get(g, 0))
ax.barh(range(5), [cnt.get(g, 0) for g in rows], color=[GCOL[g] for g in rows], height=.7)
ax.set_yticks(range(5)); ax.set_yticklabels([GLAB[g] for g in rows], fontsize=11.5)
for k, g in enumerate(rows): ax.text(cnt.get(g, 0) + .8, k, str(cnt.get(g, 0)), va="center", fontsize=11, family=MONO)
ax.set_xlabel("vice counties whose signature animal is in the group", fontsize=10, family=MONO, color=MUT); ax.tick_params(axis="y", length=0)
save(fig, os.path.join(BLOG, "b_groups.png"))

# paper figures: same images
for k, n in enumerate(["b_signature_map", "b_strongest", "b_groups", "b_distinct_map", "b_newcomers", "b_effort_map"], 1):
    shutil.copy(os.path.join(BLOG, n + ".png"), os.path.join(PAP, f"fig{k}_{n[2:]}.png"))

# header card 1200 x 630
fig = plt.figure(figsize=(12, 6.3)); fig.patch.set_facecolor(BG)
ax = fig.add_axes([.60, .02, .38, .96]); draw_counties(ax, sig_colour, lw=.35)
fig.text(.05, .80, "Signature", fontproperties=DISP, fontsize=64, color=FG, va="top")
fig.text(.05, .63, "species", fontproperties=DISP, fontsize=64, color=MOSS, va="top")
fig.text(.05, .40, "What makes your county's wildlife special?\nThe species each vice county records far more\noften than Britain and Northern Ireland as a whole.", family=SER, fontsize=17, color=FG, va="top", linespacing=1.35)
fig.text(.05, .12, f"{R['meta']['records_in_vcs'] / 1e6:.1f} million open NBN Atlas records since 2000  ·  {R['meta']['counties']} vice counties", family=MONO, fontsize=11.5, color=MUT)
fig.text(.05, .07, "Dr Tristan Hotham  ·  maps.tristanhotham.com/county-wildlife", family=MONO, fontsize=11.5, color=MUT)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100); plt.close(fig)
print("done")
