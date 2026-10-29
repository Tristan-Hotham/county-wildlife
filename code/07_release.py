"""Blog post (release/blog/post.html, meta.json) and Zenodo files (release/zenodo/)."""
import json, os, sys, re, shutil, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
R = json.load(open(os.path.join(DATA, 'results.json')))
V = json.load(open(os.path.join(ROOT, 'work', 'text_values.json')))
REL = os.path.join(ROOT, 'release'); NAME = 'Hotham_Signature_Species'
AI = "I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results."
def P(t): return f'<!-- wp:paragraph -->\n<p>{t}</p>\n<!-- /wp:paragraph -->\n\n'
def H(t, l=2): return f'<!-- wp:heading{"" if l == 2 else " {\"level\":%d}" % l} -->\n<h{l} class="wp-block-heading">{t}</h{l}>\n<!-- /wp:heading -->\n\n'
def IMG(f, alt, cap=''): return f'<!-- wp:image {{"sizeSlug":"full"}} -->\n<figure class="wp-block-image size-full">{{{{IMG|{f}|{alt}|{cap}}}}}</figure>\n<!-- /wp:image -->\n\n'
def BTN(items):
    b = ''.join(f'<!-- wp:button -->\n<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="{u}">{t}</a></div>\n<!-- /wp:button -->\n' for t, u in items)
    return f'<!-- wp:buttons -->\n<div class="wp-block-buttons">{b}</div>\n<!-- /wp:buttons -->\n\n'
v = V
inter, paper, code = ('Explore the interactive version', PAGE), ('Read the paper', f'https://doi.org/{DOI}'), ('Data and code', REPO)
post = (P(f"<em>Every county has a creature that seems to belong to it. I sorted {v['records_m']} million open wildlife records into Britain and Northern Ireland's {v['counties']} vice counties to find each one's signature species.</em>")
 + BTN([inter, paper])
 + P("Ask anyone who walks, birds or botanises what is special about their county and you will get an answer straight away. Pembrokeshire has its shearwaters. The Broads have swallowtails. The Hebrides have corncrakes, rasping away in the iris beds at night. I wanted to know whether the records themselves give the same answers when every county is treated in exactly the same way, and what else turns up.")
 + P(f"The National Biodiversity Network's Atlas gathers wildlife sightings from hundreds of recording schemes, societies, records centres and volunteers. I took only the records that are openly licensed, identified to species and dated 2000 or later: {v['records']} of them in the vice counties, the fixed recording areas naturalists have used since the nineteenth century. Then I asked one question of each county: which species make up a much bigger share of its records than they do nationally?")
 + H("A signature for every county")
 + IMG('b_signature_map.png', "Map of the vice counties of Britain and Northern Ireland, each coloured by the group of its signature animal (birds blue, mammals brown, butterflies orange, dragonflies teal, amphibians and reptiles green) and labelled with the species, such as Corncrake in the Mid Ebudes and Manx Shearwater in Pembrokeshire.", "Each vice county's signature animal: the species most over-represented in its records, against the UK. Stronger colour means a stronger signal.")
 + P(f"The measure is a location quotient. If corncrakes are a hundred times as large a slice of a county's bird records as of all bird records, the quotient is 100. Using shares rather than raw counts matters, because recording effort is wildly uneven: {v['eff_max_name']} has {v['eff_max']} open records per square kilometre since 2000 and {v['eff_min_name']} has {v['eff_min']}. Comparing each species with the rest of its own group in the same county cancels most of that out.")
 + P(f"The map reads like a naturalist's gazetteer. The corncrake makes up {v['corn_lq']} times its national share of bird records in the Mid Ebudes (Mull, Coll, Tiree and their neighbours). The Manx shearwater is {v['manx_lq']} times over-represented in Pembrokeshire, the crested tit {v['crest_lq']} times in Moray, the chough {v['chough_lq']} times in Caernarvonshire and the cirl bunting {v['cirl_lq']} times in South Devon. The swallowtail scores {v['swal_lq']} in East Norfolk, the Glanville fritillary {v['glan_lq']} on the Isle of Wight.")
 + IMG('b_strongest.png', "Lollipop chart of the sixteen strongest signature animals on a log scale, led by the mountain ringlet in Mid Perthshire at 906 times and the chequered skipper in West Inverness-shire and Argyll.", "The strongest signatures: share of the county's records of the group divided by the national share (log scale).")
 + f'<!-- wp:pullquote -->\n<figure class="wp-block-pullquote"><blockquote><p>The mountain ringlet makes up {v["ring_lq"]} times as large a share of butterfly records in Mid Perthshire as it does across the UK.</p></blockquote></figure>\n<!-- /wp:pullquote -->\n\n'
 + H("Birds, then mammals, then butterflies")
 + P(f"A bird is the signature animal of {v['n_birds']} counties, a mammal of {v['n_mammals']}, a butterfly of {v['n_butterflies']}, a dragonfly of {v['n_dragonflies']} and an amphibian or reptile of {v['n_herps']}. The Scotch argus, a dark brown butterfly of Scottish grassland, is the signature of {v['scotch_argus_n']} counties, more than any other species, and the hooded crow is the signature bird of {v['hooded_ni']} of Northern Ireland's six.")
 + IMG('b_groups.png', f"Bar chart: birds are the signature animal of {v['n_birds']} vice counties, mammals {v['n_mammals']}, butterflies {v['n_butterflies']}, dragonflies {v['n_dragonflies']}, amphibians and reptiles {v['n_herps']}.", "")
 + P(f"Some signatures are animals people brought. Chinese water deer top the list in Huntingdonshire ({v['cwd_lq']} times), wild boar in West Gloucestershire, home of the Forest of Dean ({v['boar_lq']}), wall lizards on the Isle of Wight and stoats on Orkney ({v['stoat_lq']}). And because records just offshore count for the county, dolphins, porpoises and seals turn up as coastal signatures.")
 + H("The least typical counties")
 + P(f"I also measured how different each county's whole list is from the national mix, after taking away the difference a random sample of the same size would show by chance. {v['dist_top']}, {v['dist_2']} and the {v['dist_3']} are the most distinctive; {v['dist_low']} and {v['dist_low2']} the most ordinary. On average Scotland's counties score {v['dist_sco']} on this measure and England's {v['dist_eng']}.")
 + IMG('b_distinct_map.png', "Map shaded from pale green for counties whose animal records look like the national mix to dark green for distinctive ones; the northern isles, Hebrides and Highlands are darkest and the English Midlands palest.", "How far each county's animal records differ from the national mix, beyond chance.")
 + H("Newcomers on the move")
 + P(f"The same records catch species arriving. The harlequin ladybird, first found in Britain in 2004, had records in {v['harl_2']} vice counties in 2000 to 2009 and {v['harl_4']} since 2020. The tree bumblebee, which flew in from the continent on its own, went from {v['tree_2']} to {v['tree_4']}. The little egret, a rarity before the 1990s, now turns up in {v['egret_4']}, and the ring-necked parakeet has spread from {v['para_2']} counties to {v['para_4']}.")
 + IMG('b_newcomers.png', "Ten small bar charts showing vice counties with at least two records per period from the 1970s to the 2020s for harlequin ladybird, tree bumblebee, ring-necked parakeet, Egyptian goose, little egret, Cetti's warbler, small red-eyed damselfly, Reeves' muntjac, grey squirrel and red squirrel.", "Vice counties with at least two open records in each period. Recording has grown too, so read these as a lower bound on spread.")
 + H("Records are not wildlife")
 + P(f"Every record is a moment when someone looked, saw and wrote it down, so a map of records is partly a map of recorders. The busiest counties are around London; the quietest are in the north west Highlands and Northern Ireland, a {v['eff_ratio']}-fold difference per square kilometre.")
 + IMG('b_effort_map.png', "Map of open records per square kilometre since 2000: dark blue across south east England, pale in the Scottish Highlands and Northern Ireland.", "Open records per square kilometre since 2000.")
 + P("The quotients cancel out the overall level of effort, but not a big survey of one species, a rare bird that drew a crowd, or a scheme that keeps its data under a non-commercial licence. Treat a signature as \"recorded unusually often here\", not as a census. The interactive map lets you check: tap a county to see its top species in each group, the datasets behind it, and the species recorded nowhere else.")
 + H("How I did this")
 + P(f"I queried the NBN Atlas web service for counts only, never individual records, so nothing here pinpoints a sensitive species. I kept records under CC0, CC BY and the Open Government Licence ({v['records_open']} in all) and left out CC BY NC data. A species needed at least {v['min_sp_vc']} records in a county and {v['min_sp_uk']} nationally to be ranked, a group needed {v['min_group']} records in a county ({v['min_group_small']} for mammals, amphibians and reptiles, and dragonflies), and I ranked by a cautious version of the quotient that discounts small counts. Vice county boundaries come from the Biological Records Centre and, for Northern Ireland, OpenStreetMap.")
 + BTN([inter, paper, code])
 + H("Notes and sources", 3)
 + '<!-- wp:list -->\n<ul class="wp-block-list">\n'
 + f'<li>Records: <a href="https://nbnatlas.org">NBN Atlas</a>, occurrence web services, retrieved {v["retrieved"]}; only records licensed CC0, CC BY 4.0 or OGL v3, with thanks to all data providers.</li>\n'
 + '<li>Boundaries: Biological Records Centre, <a href="https://github.com/BiologicalRecordsCentre/vice-counties">Watsonian vice counties</a> (GPL 3.0); <a href="https://github.com/SK53/Irish-Vice-Counties">Irish vice counties</a> from OpenStreetMap contributors (ODbL).</li>\n'
 + '<li>Place names on the map: <a href="https://www.geonames.org">GeoNames</a> (CC BY 4.0).</li>\n'
 + f'<li>Paper, data and code: <a href="https://doi.org/{DOI}">Zenodo</a> and <a href="{REPO}">GitHub</a>.</li>\n'
 + f'<li>{AI}</li>\n</ul>\n<!-- /wp:list -->\n')
open(os.path.join(REL, 'blog', 'post.html'), 'w').write(post)
meta = {"title": "Signature species: what makes your county's wildlife special?", "slug": SLUG,
        "excerpt": f"I sorted {v['records_m']} million open wildlife records into {v['counties']} vice counties to find the species each one records far more often than the rest of Britain and Northern Ireland.",
        "seo_description": "Every county's signature species from open NBN Atlas records: corncrakes, shearwaters, choughs and swallowtails, mapped by location quotient.",
        "tags": ["wildlife", "biodiversity", "NBN Atlas", "maps", "vice counties", "data visualisation", "birds", "butterflies"],
        "header_alt": "Signature species: a map of Britain and Northern Ireland's vice counties coloured by the group of each county's most over-represented animal."}
json.dump(meta, open(os.path.join(REL, 'blog', 'meta.json'), 'w'), indent=1, ensure_ascii=False)
words = len(re.sub(r'<[^>]+>|\{\{IMG[^}]*\}\}', ' ', post).split())
# Zenodo
Z = os.path.join(REL, 'zenodo')
shutil.copy(os.path.join(REL, NAME + '.pdf'), Z)
for f in ['counties.csv', 'signature_species.csv', 'only_here.csv', 'newcomers.csv']: shutil.copy(os.path.join(DATA, f), Z)
with zipfile.ZipFile(os.path.join(Z, f'{SLUG}_code_and_data.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for d in ['code', 'data']:
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            p = os.path.join(ROOT, d, fn)
            if os.path.isfile(p) and not fn.endswith('.pyc'): z.write(p, f'{SLUG}/{d}/{fn}')
    for fn in ['README.md', 'LICENSE']: z.write(os.path.join(ROOT, fn), f'{SLUG}/{fn}')
tex = open(os.path.join(REL, 'paper', NAME + '.tex')).read()
ab = re.search(r'\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n', tex, re.S).group(1).replace('\\%', '%').replace('\\&', '&')
zmeta = {"title": "Signature Species: What Makes Each County's Wildlife Special? Location Quotients from Open Biological Records",
         "description_html": f"<p>{ab}</p><p>Interactive version: {PAGE}. Data and code: {REPO}. Blog post: to follow.</p>",
         "keywords": ["biological records", "vice counties", "location quotient", "NBN Atlas", "recording effort", "biodiversity", "Britain", "Northern Ireland", "open data", "signature species"],
         "licence": "cc-by-4.0",
         "related": [{"identifier": REPO, "relation": "issupplementedby", "resource_type": "software"},
                     {"identifier": PAGE, "relation": "issupplementedby", "resource_type": "other"},
                     {"identifier": "https://nbnatlas.org", "relation": "isderivedfrom", "resource_type": "dataset"},
                     {"identifier": "https://github.com/BiologicalRecordsCentre/vice-counties", "relation": "isderivedfrom", "resource_type": "dataset"},
                     {"identifier": "https://github.com/SK53/Irish-Vice-Counties", "relation": "isderivedfrom", "resource_type": "dataset"},
                     {"identifier": "https://www.geonames.org", "relation": "isderivedfrom", "resource_type": "dataset"}]}
json.dump(zmeta, open(os.path.join(Z, 'meta.json'), 'w'), indent=1, ensure_ascii=False)
print('blog words', words, 'abstract words', len(ab.split()))
