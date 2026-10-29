"""Write release/paper/Hotham_Signature_Species.tex from results.json and compile with xelatex."""
import json, os, sys, subprocess, re, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
R = json.load(open(os.path.join(DATA, 'results.json')))
V = json.load(open(os.path.join(ROOT, 'work', 'text_values.json')))
M = R['meta']; S = R['signature']
PAP = os.path.join(ROOT, 'release', 'paper'); NAME = 'Hotham_Signature_Species'
def tx(s): return str(s).replace('&', '\\&').replace('%', '\\%').replace('#', '\\#').replace('_', '\\_')
def n0(x): return f"{round(x):,}"
def lq(x): return f"{x:,.0f}" if x >= 10 else f"{x:.1f}"
GL = {k: l for k, l, _ in GROUPS}

# Table 1: groups
t1 = "\n".join(f"{GL[g]} & {n0(R['groups'][g]['records'])} & {n0(R['groups'][g]['species'])} & {R['groups'][g]['counties_shown']} \\\\" for g, _, _ in GROUPS)
# Table 2: selected signatures
sel = [('Mid Ebudes', 'birds'), ('West Ross', 'birds'), ('Moray', 'birds'), ('Pembrokeshire', 'birds'), ('Caernarvonshire', 'birds'), ('South Devon', 'birds'), ('South Wiltshire', 'birds'),
       ('Mid Perthshire', 'butterflies'), ('West Inverness-shire', 'butterflies'), ('East Norfolk', 'butterflies'), ('Isle of Wight', 'butterflies'),
       ('Huntingdonshire', 'mammals'), ('West Gloucestershire', 'mammals'), ('Orkney', 'mammals'), ('West Norfolk', 'herps'), ('Dorset', 'herps'), ('Antrim', 'birds')]
t2 = "\n".join(f"{tx(c)} & {GL[g]} & {tx(S[c][g][0])} & {n0(S[c][g][2])} & {lq(S[c][g][1])} \\\\" for c, g in sel)
# Table 3: newcomers
P = R['periods']
t3 = "\n".join(f"{tx(r['species'])} & {r['status']} & " + " & ".join(str(r['vc_' + p]) for p in P) + " \\\\" for r in R['newcomers'])
da = R['distinct_animals']
dtop = ", ".join(f"{tx(a)} ({b:.2f})" for a, b in da[:5]); dlow = ", ".join(f"{tx(a)} ({b:.2f})" for a, b in da[-5:][::-1])
eff_top = ", ".join(f"{tx(a)} ({n0(b)})" for a, b in R['effort']['most_per_km2'][:3]); eff_low = ", ".join(f"{tx(a)} ({n0(b)})" for a, b in R['effort']['least_per_km2'][:3])
pt = M['period_totals']; ptx = "; ".join(f"{k.replace('-', ' to ')}: {n0(v['total'])}" for k, v in pt.items())
v = {k: tx(x) for k, x in V.items()}
abstract = (f"Naturalists have long recorded wildlife by vice county, the fixed recording areas of Britain and Ireland, and the NBN Atlas now publishes hundreds of millions of these records. "
  f"I ask what makes each county's wildlife distinctive. Using only openly licensed (CC0, CC BY and Open Government Licence) records identified to species, marked present and dated 2000 or later, I count {v['records']} records of {v['species']} species in the {v['counties']} vice counties of Great Britain, the Isle of Man and Northern Ireland, and compute for each species a location quotient: its share of a group's records in a county divided by its share of that group's records everywhere. "
  f"To avoid tiny-sample artefacts I require {v['min_sp_vc']} county records and {v['min_sp_uk']} records in all, and rank species by the lower bound of a {v['ci']}\\% Poisson interval. "
  f"The resulting signature species are recognisable: the corncrake in the Mid Ebudes ({v['corn_lq']} times its national share of bird records), the Manx shearwater in Pembrokeshire ({v['manx_lq']}), the crested tit in Moray ({v['crest_lq']}) and the mountain ringlet in Mid Perthshire ({v['ring_lq']}). "
  f"A bird is the signature animal of {v['n_birds']} counties, a mammal of {v['n_mammals']} and a butterfly of {v['n_butterflies']}. A chance-corrected distinctiveness index puts the northern isles and the Hebrides at the top and the English Midlands at the bottom. "
  f"Recording effort varies {v['eff_ratio']}-fold per square kilometre, and the quotients describe records, not populations.")
tex = r"""\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}
\setmainfont{TeX Gyre Pagella}
\newfontfamily\headfont{Inter}[UprightFont=*-ExtraBold,BoldFont=*-ExtraBold,Extension=.otf,Path=/usr/share/fonts/opentype/inter/]
\usepackage[a4paper,margin=2.3cm]{geometry}
\usepackage{graphicx,booktabs,float,caption,array}
\usepackage[hidelinks]{hyperref}
\usepackage{titlesec}
\usepackage{setspace}
\setstretch{1.05}
\renewcommand{\topfraction}{0.9}\renewcommand{\bottomfraction}{0.8}\renewcommand{\textfraction}{0.1}\renewcommand{\floatpagefraction}{0.75}
\setlength{\parindent}{0pt}\setlength{\parskip}{0.55em}
\titleformat{\section}{\headfont\Large}{\thesection}{0.8em}{}
\titleformat{\subsection}{\headfont\large}{\thesubsection}{0.8em}{}
\captionsetup{font=small,labelfont=bf}
\urlstyle{same}
\hypersetup{pdftitle={Signature Species: What Makes Each County's Wildlife Special},pdfauthor={Tristan Hotham}}
\begin{document}
\begin{center}
{\Large\bfseries Signature Species:\\[2pt] What Makes Each County's Wildlife Special?\\[2pt] Location Quotients from Open Biological Records\par}
\vspace{1.2em}
{\large Tristan Hotham\par}
\vspace{0.3em}
{\small Independent researcher\\ ORCID: 0000-0003-4931-9349\\ DOI: \href{https://doi.org/@DOI@}{https://doi.org/@DOI@}\par}
\vspace{0.8em}
2026
\end{center}
\begin{quote}\small
\begin{center}\textbf{Abstract}\end{center}
@ABSTRACT@

\textbf{Keywords:} biological records; vice counties; location quotient; NBN Atlas; recording effort; open data; Britain; Northern Ireland; signature species; interactive map
\end{quote}

\section{Introduction}
Ask a naturalist what is special about a county and the answer comes quickly: Pembrokeshire has its seabird islands, the Norfolk Broads their swallowtails, the Hebrides their corncrakes, Anglesey and Caernarvonshire their choughs. These answers are local knowledge built up over generations of recording. This note asks whether the same answers fall out of the records themselves when every county is treated in the same way, and what else turns up.

The question is harder than it looks, for two reasons. First, the raw number of records of a species in a county mostly measures how many people record there: some counties have twenty or more times as many records per square kilometre as others. Second, groups of species are recorded by different schemes and with very different intensity, so a county with an active bird club looks rich in birds whatever lives there. I deal with both by working with shares: each species' share of its own group's records in a county, against the same share nationally. That ratio, a location quotient, is a standard tool for describing regional specialisation in economics \cite{isard}, and here it asks whether a county's recorders see a species unusually often relative to everything else they see in the same group.

The results are published as an interactive map at \url{https://maps.tristanhotham.com/county-wildlife/}, where any of @picker@ species can be mapped, and every number here comes from the data files in the accompanying repository.

\section{Data}
\subsection{Records}
The NBN Atlas \cite{nbn} is the United Kingdom's national aggregator of biological records, holding sightings from recording schemes, societies, local environmental records centres, statutory agencies and citizen science platforms. Each record keeps the licence chosen by its provider. I queried the Atlas's occurrence web service on @retrieved@ using facet queries only: for each vice county, the number of records of every taxon, never the records themselves. I kept records that are (i) identified to the rank of species, (ii) marked as present rather than absent, (iii) dated 2000 or later and (iv) published under CC0, CC BY or the Open Government Licence. Together these give @records_open@ records (@cc_by@ under CC BY, @ogl@ under OGL and @cc0@ under CC0), of which @records@ fall in one of the vice counties used here. Records under CC BY NC, which include some large national schemes, are excluded, which makes some groups thin, especially moths.

\subsection{Vice counties}
The units are the Watsonian vice counties of Great Britain, numbered 1 to 112 and including the Isle of Man (VC 71), defined in the nineteenth century to give botanists stable recording areas of roughly equal size \cite{watson}, and the six Irish vice counties of Northern Ireland (H33, H36 to H40) from Praeger's scheme \cite{praeger}. The Atlas assigns records to them spatially. For mapping I simplified the vice county boundaries published by the Biological Records Centre \cite{brcvc} and the Irish vice counties traced in OpenStreetMap \cite{sk53}. Areas are measured on the British National Grid.

\subsection{Groups}
I used seven groups: birds, mammals, amphibians and reptiles, butterflies, moths, dragonflies and damselflies, and flowering plants, taken from the Atlas's species groups; butterflies are the six butterfly families of Lepidoptera and moths are the rest. Eight domestic or feral domestic taxa (for example domestic cattle and the swan goose, whose domestic form escapes widely) were dropped. Table~\ref{tab:groups} summarises the groups.

\begin{table}[H]\centering\small
\caption{Open records since 2000 in the vice counties, by group, and the number of vice counties with enough records of the group to rank its species.}\label{tab:groups}
\begin{tabular}{lrrr}\toprule
Group & Records & Species & Counties ranked \\\midrule
@T1@
\bottomrule\end{tabular}
\end{table}

\section{Methods}
\subsection{Location quotients}
For species $s$ in group $g$ and county $c$, with $n_{sc}$ records of the species in the county, $N_{gc}$ records of the group in the county, $N_s$ records of the species in all counties and $N_g$ of the group,
\[ \mathrm{LQ}_{sc} = \frac{n_{sc}/N_{gc}}{N_s/N_g}. \]
A quotient of 10 means the species is ten times as large a slice of the county's records of its group as of the national records of that group. Because the denominator is the county's own total for the group, the overall level of recording effort cancels out; what remains is the mix of species recorded.

\subsection{Thresholds}
Quotients are unstable when counts are small: a single vagrant seen by a few observers can produce a very large ratio. I therefore only rank a species in a county if it has at least @min_sp_vc@ records there and at least @min_sp_uk@ in all counties, and only rank a group in a county with at least @min_group@ records of that group (@min_group_small@ for the three smallest groups: mammals, amphibians and reptiles, and dragonflies). Within those limits I rank species by a cautious quotient that replaces $n_{sc}$ with the lower bound of a two-sided @ci@\% Poisson interval, so that a quotient based on 25 records must be much larger than one based on 2,500 to rank above it. The plain quotient is reported throughout. A county's \emph{signature animal} is the highest-ranked species across birds, mammals, amphibians and reptiles, butterflies, and dragonflies.

\subsection{Distinctiveness}
To compare whole species lists I use the total variation distance between a county's species shares within a group and the national shares: half the sum of absolute differences, from 0 (identical mix) to 1 (no shared species). A county with few records will differ from the national mix by chance, so I subtract the mean distance of 20 random multinomial samples of the same size drawn from the national shares, and average the resulting excess over the five animal groups that pass the thresholds.

\subsection{Single-county species and newcomers}
A species is counted as recorded in only one county if it has at least @only_min@ records since 2000, all from the same vice county. For a set of ten species that have spread or changed in recent decades I also counted, in five periods (1970 to 1989, 1990 to 1999, 2000 to 2009, 2010 to 2019 and 2020 to 2026), the vice counties with at least two open records; these queries used all taxonomic ranks of the species.

\section{Results}
\subsection{Signature species}
Figure~\ref{fig:map} maps each county's signature animal and Table~\ref{tab:sig} lists a selection by group. The list reads like a naturalist's gazetteer. The corncrake makes up @corn_lq@ times its national share of bird records in the Mid Ebudes (@corn_n@ records), the Manx shearwater @manx_lq@ times in Pembrokeshire, the crested tit @crest_lq@ times in Moray, the chough @chough_lq@ times in Caernarvonshire, and the cirl bunting @cirl_lq@ times in South Devon, the county where conservation work has concentrated the species. Among butterflies, the mountain ringlet in Mid Perthshire (@ring_lq@) and the chequered skipper in West Inverness-shire (@cheq_lq@) are the strongest signals on the map, followed by the swallowtail in East Norfolk (@swal_lq@) and the Glanville fritillary on the Isle of Wight (@glan_lq@).

\begin{figure}[H]\centering
\includegraphics[width=0.72\textwidth]{fig1_signature_map.png}
\caption{Signature animal of each vice county: the species with the highest cautious location quotient across birds, mammals, amphibians and reptiles, butterflies, and dragonflies. Colour shows the group, strength the size of the quotient. Labels show the plain quotient where space allows.}\label{fig:map}
\end{figure}

\begin{table}[H]\centering\small
\caption{Selected signature species by group: county, records since 2000 and location quotient.}\label{tab:sig}
\begin{tabular}{lllrr}\toprule
Vice county & Group & Species & Records & LQ \\\midrule
@T2@
\bottomrule\end{tabular}
\end{table}

A bird is the signature animal of @n_birds@ counties, a mammal of @n_mammals@, a butterfly of @n_butterflies@, a dragonfly or damselfly of @n_dragonflies@ and an amphibian or reptile of @n_herps@ (Figure~\ref{fig:groups}). The Scotch argus is the commonest single signature, in @scotch_argus_n@ Scottish counties, and the hooded crow is the signature bird of @hooded_ni@ of the six Northern Irish vice counties. Several signatures are introduced animals with restricted ranges: Chinese water deer in the fens (Huntingdonshire, @cwd_lq@), wild boar in West Gloucestershire, the Forest of Dean (@boar_lq@), wall lizards on the Isle of Wight, sika deer in Dorset and stoats on Orkney (@stoat_lq@). Coastal counties pick up marine mammals because records just offshore fall inside the vice county boundaries used by the Atlas.

\begin{figure}[H]\centering
\includegraphics[width=0.85\textwidth]{fig2_strongest.png}
\caption{The sixteen strongest signature animals (plain location quotient, log scale), coloured by group.}\label{fig:strong}
\end{figure}

\begin{figure}[H]\centering
\includegraphics[width=0.8\textwidth]{fig3_groups.png}
\caption{Number of vice counties whose signature animal belongs to each group.}\label{fig:groups}
\end{figure}

\subsection{Distinctiveness}
After correcting for sample size, the most distinctive counties across the animal groups are @DTOP@. The least distinctive are @DLOW@ (Figure~\ref{fig:dist}). The mean is @dist_sco@ for Scotland's vice counties, @dist_ni@ for Northern Ireland's, @dist_wal@ for Wales's and @dist_eng@ for England's. The pattern is what biogeography would predict: island and northern faunas lack many widespread southern species and hold northern and maritime ones, while lowland English counties share most of the national list.

\begin{figure}[H]\centering
\includegraphics[width=0.62\textwidth]{fig4_distinct_map.png}
\caption{Distinctiveness of each county's animal records: total variation distance from the national species mix minus its expected value under random sampling, averaged over five animal groups.}\label{fig:dist}
\end{figure}

\subsection{Single-county species}
@only_total@ species in the seven groups have at least @only_min@ records since 2000, all from one vice county: @only_plants@ plants and @only_moths@ moths, the rest animals. Many are escapes, introductions or recent colonists rather than relicts. The animal cases include a long-staying greater mouse-eared bat in West Sussex, a black-browed albatross in South-east Yorkshire, a veery on Orkney and several escaped exotic birds. @only_top@ and @only_top2@ have the most single-county species (@only_top_n@ each).

\subsection{Newcomers}
Table~\ref{tab:new} and Figure~\ref{fig:new} show the number of vice counties with at least two records of ten species by period. The harlequin ladybird, first found in Britain in 2004, had records in @harl_2@ vice counties in 2000 to 2009 and @harl_4@ in 2020 to 2026; the tree bumblebee, a natural colonist, went from @tree_2@ to @tree_4@; the little egret from @egret_0@ in 1970 to 1989 to @egret_4@; and the ring-necked parakeet from @para_2@ in 2000 to 2009 to @para_4@. Grey squirrels are recorded in nearly every county in every period, and red squirrels in a stable set of around sixty. These counts must be read against the growth of recording itself: open records numbered @PT@.

\begin{table}[H]\centering\small
\caption{Vice counties with at least two open records, by period.}\label{tab:new}
\begin{tabular}{llrrrrr}\toprule
Species & Status & 1970 to 1989 & 1990s & 2000s & 2010s & 2020 to 2026 \\\midrule
@T3@
\bottomrule\end{tabular}
\end{table}

\begin{figure}[H]\centering
\includegraphics[width=0.9\textwidth]{fig5_newcomers.png}
\caption{Vice counties with at least two open records of ten spreading or changing species, by period.}\label{fig:new}
\end{figure}

\subsection{Recording effort}
Open records per square kilometre since 2000 range from @EFFLOW@ at the bottom to @EFFTOP@ at the top, a @eff_ratio@-fold spread around a median of @eff_median@ (Figure~\ref{fig:eff}). Effort is highest around London and the south east and lowest in the north west Highlands and in Northern Ireland.

\begin{figure}[H]\centering
\includegraphics[width=0.62\textwidth]{fig6_effort_map.png}
\caption{Open NBN Atlas records per square kilometre since 2000, by vice county (log colour scale).}\label{fig:eff}
\end{figure}

\section{Discussion}
The location quotient recovers local knowledge with little tuning. Most signatures are species with small ranges that are well recorded where they occur: mountain and moorland specialists in the Highlands, seabirds at their colonies, the cirl bunting and Dartford warbler on the south coast, the stone-curlew on Salisbury Plain and in Breckland. The method's value is less in confirming these than in making every county comparable and searchable, and in showing the second and third species behind the obvious one. In Pembrokeshire, for example, the Manx shearwater is followed by the puffin and razorbill among birds, the greater horseshoe bat among mammals, the southern damselfly among dragonflies and the Tenby daffodil among plants; each is a reasonable answer to the question of what the county is known for, and the ranked lists make it easy to see which answer depends on the group one chooses.

The same ratio also exposes the geography of recording. The least recorded counties produce the strongest quotients, because their species lists are short and dominated by a few specialists, while the busiest counties of the south east look ordinary because their recorders see a bit of everything. Correcting the distinctiveness index for sample size removes the purely statistical part of this effect, but the remaining contrast between north and south is real and large.

Three kinds of signal need care. The first is targeted recording: a big survey of one species can inflate its quotient in one county. Some mammal signatures (water vole in North Lincolnshire, bank vole in County Durham, mole in South-east Yorkshire) probably reflect particular projects as much as the animals. The second is attraction: rarities, escapes and vagrants that draw many observers to one place produce many records of one individual. The thresholds and the cautious ranking reduce this but do not remove it. The third is licensing: because CC BY NC data are excluded, the open record set over-represents schemes and regions that publish openly, and moths in particular rest on a fraction of the national data.

\section{Limitations}
Records are presence-only observations submitted by people who chose where and what to record; they are not a survey, and their biases in space, time and taxon are well documented \\cite{isaac}. Location quotients describe the composition of records, not abundance or range. Vice county boundaries include some inshore waters, so marine species appear as coastal signatures. Plant records in the Atlas are dominated by the BSBI Plant Atlas 2020 \cite{plantatlas}, whose records are grid-square occurrences by period rather than individual sightings. Records identified only to subspecies or aggregate are not included. Counts were retrieved on a single date and will change as the Atlas grows. The newcomers counts use a two-record threshold per period and periods of unequal length. Finally, the NBN Atlas already generalises the locations of sensitive species; only county-level counts are published here.

\section{Conclusion}
Treating every county the same way, open biological records give each part of Britain and Northern Ireland a recognisable signature, and a ranked list behind it. The strongest signals come from the mountains and islands of the north and west, which are also the least recorded places, while the most heavily recorded counties of the south east are the most typical. The interactive map lets anyone ask the same question of their own county, and of any of @picker@ species.

\section*{Data and code availability}
Code and derived data (county tables, species ranks, single-county species, newcomers, boundaries) are at \url{https://github.com/Tristan-Hotham/county-wildlife} and archived with this paper at \url{https://doi.org/@DOI@}. The interactive page is at \url{https://maps.tristanhotham.com/county-wildlife/}. Record counts derive from openly licensed NBN Atlas records (CC0, CC BY 4.0, OGL v3) with attribution to the NBN Atlas and its data providers. Boundaries: Biological Records Centre (GPL 3.0) and OpenStreetMap contributors (ODbL).

\section*{AI statement}
I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.

\begin{thebibliography}{9}\small
\bibitem{brcvc} Biological Records Centre (2019) Watsonian vice county boundaries GIS layers. \url{https://github.com/BiologicalRecordsCentre/vice-counties}.
\bibitem{isaac} Isaac, N.J.B. and Pocock, M.J.O. (2015) Bias and information in biological records. \emph{Biological Journal of the Linnean Society} 115, 522 to 531.
\bibitem{isard} Isard, W. (1960) \emph{Methods of Regional Analysis: An Introduction to Regional Science}. Cambridge, MA: MIT Press.
\bibitem{nbn} NBN Atlas. National Biodiversity Network. \url{https://nbnatlas.org}; occurrence web services \url{https://records-ws.nbnatlas.org}. Accessed @retrieved@.
\bibitem{sk53} OpenStreetMap contributors, Irish vice counties. \url{https://github.com/SK53/Irish-Vice-Counties} (ODbL).
\bibitem{praeger} Praeger, R.L. (1901) Irish Topographical Botany. \emph{Proceedings of the Royal Irish Academy} 7.
\bibitem{plantatlas} Stroh, P.A. et al. (2023) \emph{Plant Atlas 2020: Mapping Changes in the Distribution of the British and Irish Flora}. Princeton: Princeton University Press.
\bibitem{watson} Watson, H.C. (1852) \emph{Cybele Britannica}, volume 3. London: Longman.
\end{thebibliography}
\end{document}
"""
rep = {'ABSTRACT': abstract, 'T1': t1, 'T2': t2, 'T3': t3, 'DTOP': dtop, 'DLOW': dlow, 'EFFTOP': eff_top, 'EFFLOW': eff_low, 'PT': ptx, 'DOI': DOI}
rep.update(v)
tex = re.sub(r'@(\w+)@', lambda m: str(rep[m.group(1)]), tex)
open(os.path.join(PAP, NAME + '.tex'), 'w').write(tex)
for _ in range(2):
    r = subprocess.run(['xelatex', '-interaction=nonstopmode', NAME + '.tex'], cwd=PAP, capture_output=True, text=True)
for ext in ['aux', 'log', 'out']:
    p = os.path.join(PAP, NAME + '.' + ext)
    if os.path.exists(p): os.remove(p)
shutil.move(os.path.join(PAP, NAME + '.pdf'), os.path.join(ROOT, 'release', NAME + '.pdf'))
print('ok', r.returncode)
