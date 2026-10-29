"""Shared settings for the county-wildlife analysis."""
import os
BUNDLE = os.environ.get('CW_BUNDLE', '/home/claude/hist/_data18/county-wildlife/cw_nbn_vc_2026.json.gz')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
DOI = '10.5281/zenodo.23761435'
SLUG = 'county-wildlife'
PAGE = 'https://maps.tristanhotham.com/county-wildlife/'
REPO = 'https://github.com/Tristan-Hotham/county-wildlife'
BLOG = 'https://blog.tristanhotham.com/2026/10/29/county-wildlife/'

# thresholds (stated on the page and in the paper)
MIN_SP_VC = 20        # a species needs at least this many records in a county to count as over-represented there
MIN_SP_UK = 200       # and at least this many records across Britain and Northern Ireland
MIN_GROUP_VC = 1000   # a county needs at least this many records of a group for that group's signature to be shown
MIN_GROUP_VC_SMALL = 150  # for the small groups (amphibians and reptiles, mammals, dragonflies)
CI = 0.90             # conservative LQ uses the lower bound of a 90% Poisson interval on the county count
ONLY_MIN = 5          # "only here": at least this many records, all in one county

BUTTERFLY_FAMILIES = {'Hesperiidae', 'Papilionidae', 'Pieridae', 'Lycaenidae', 'Riodinidae', 'Nymphalidae'}
GROUPS = [  # key, label, colour
    ('birds', 'Birds', '#2E6FA7'),
    ('mammals', 'Mammals', '#9A4E1C'),
    ('herps', 'Amphibians and reptiles', '#4F8A2B'),
    ('butterflies', 'Butterflies', '#D9822B'),
    ('moths', 'Moths', '#7A5C99'),
    ('dragonflies', 'Dragonflies and damselflies', '#1C8C8C'),
    ('plants', 'Flowering plants', '#B8336A'),
]
SMALL_GROUPS = {'mammals', 'herps', 'dragonflies'}
