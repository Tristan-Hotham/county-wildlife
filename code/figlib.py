"""Shared drawing helpers for header, blog and paper figures and the Reddit collage (matplotlib).
Fonts: FONT_DIR with Fraunces, Source Serif 4 and IBM Plex Mono (Google Fonts, OFL); otherwise matplotlib defaults.
Maps are drawn from data/vice_counties.geojson projected to the British National Grid (no web tiles)."""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from pyproj import Transformer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts/")
DISP = None
if os.path.isdir(FD):
    for f in os.listdir(FD):
        if f.endswith(".ttf"): fm.fontManager.addfont(os.path.join(FD, f))
    if os.path.exists(os.path.join(FD, "FrauncesVar.ttf")): DISP = fm.FontProperties(fname=os.path.join(FD, "FrauncesVar.ttf"), weight=900)
SER, MONO = "Source Serif 4", "IBM Plex Mono"
BG, FG, MUT, RULE, FEW = "#F5F3E9", "#1C2620", "#5E665D", "#DCD8C6", "#DEDBCF"
MOSS, HOT = "#2F6B3A", "#C4542A"
GCOL = {k: c for k, _, c in GROUPS}
GLAB = {k: l for k, l, _ in GROUPS}
plt.rcParams.update({"font.family": SER, "font.size": 13, "axes.edgecolor": MUT, "axes.labelcolor": FG, "xtick.color": MUT, "ytick.color": MUT,
                     "axes.spines.top": False, "axes.spines.right": False, "savefig.facecolor": BG, "figure.facecolor": BG, "axes.facecolor": BG})
R = json.load(open(os.path.join(DATA, "results.json")))
PG = json.load(open(os.path.join(DATA, "page.json")))
GEO = json.load(open(os.path.join(DATA, "vice_counties.geojson")))
to_bng = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)
hexrgb = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255
def mix(a, b, t): return tuple(hexrgb(a) + (hexrgb(b) - hexrgb(a)) * t)

def county_rings():
    """{vc_id: [ring arrays in BNG km]} and {vc_id: (x, y) label point}"""
    rings, pts = {}, {}
    for f in GEO["features"]:
        g = f["geometry"]; polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        rr = []
        for p in polys:
            a = np.array(p[0]); e, n = to_bng.transform(a[:, 0], a[:, 1]); rr.append(np.c_[e, n] / 1000)
        rings[f["properties"]["id"]] = rr
        e, n = to_bng.transform(f["properties"]["lon"], f["properties"]["lat"]); pts[f["properties"]["id"]] = (e / 1000, n / 1000)
    return rings, pts
RINGS, PTS = county_rings()
CB = {c["id"]: c for c in PG["counties"]}

def draw_counties(ax, colour_of, ec="#FFFFFF", lw=.5, z=1):
    patches, fcs = [], []
    for cid, rr in RINGS.items():
        for r in rr: patches.append(Polygon(r)); fcs.append(colour_of(cid))
    ax.add_collection(PatchCollection(patches, facecolor=fcs, edgecolor=ec, linewidth=lw, zorder=z))
    ax.set_xlim(-10, 670); ax.set_ylim(0, 1225); ax.set_aspect("equal"); ax.axis("off")

def strength(lq): return max(.18, min(1, np.log10(max(lq, 1)) / np.log10(300)))
def sig_colour(cid, g="animals", bg=BG):
    c = CB[cid]
    if g == "animals":
        if not c["animal"]: return FEW
        return mix(bg, GCOL[c["animal"][5]], .22 + .78 * strength(c["animal"][3]))
    t = c["top"].get(g)
    if not t: return FEW
    return mix(bg, GCOL[g], .22 + .78 * strength(t[0][3]))

def fq(v): return f"{v:,.0f}" if v >= 10 else f"{v:.1f}"
def save(fig, path, dpi=200):
    fig.savefig(path, dpi=dpi); plt.close(fig)
