// Gathering script, run in a browser tab open on https://records-ws.nbnatlas.org/ (same origin, so no CORS issues).
// It makes facet queries only (no record downloads) and saves one gzipped JSON bundle, cw_nbn_vc_2026.json.gz.
// Retrieved 29 October 2026. Licence filter: only records under CC0, CC-BY or OGL are counted.
const enc = encodeURIComponent, sleep = ms => new Promise(r => setTimeout(r, ms));
const LIC = 'fq=' + enc('license:("CC-BY" OR "OGL" OR "CC0")');
const BASE = LIC + '&fq=' + enc('rank:species') + '&fq=' + enc('occurrence_status:PRESENT') + '&fq=' + enc('year:[2000 TO *]');
async function get(qs) {
  for (let a = 0; a < 6; a++) {
    try { const r = await fetch('/occurrences/search?q=*:*&pageSize=0&' + qs); if (r.status == 429 || r.status >= 500) { await sleep(3000 * (a + 1)); continue; }
      const j = await r.json(); if (!j.facetResults) throw new Error('no facets'); return j; } catch (e) { await sleep(3000 * (a + 1)); }
  } throw new Error('failed ' + qs);
}
const fr = (j, n) => (j.facetResults.find(x => x.fieldName == n) || { fieldResult: [] }).fieldResult;
(async () => {
  const out = { source: 'NBN Atlas occurrence web services, https://records-ws.nbnatlas.org/occurrences/search (facet queries)', licence: 'CC0, CC-BY and OGL records only', retrieved: new Date().toISOString(), base_filters: decodeURIComponent(BASE), sp_list: [], vc: {}, groups: {}, subgroups: {}, invasive: {} };
  const sidx = {};
  const addSp = label => { const p = label.split('|'); if (!(p[1] in sidx)) { sidx[p[1]] = out.sp_list.length; out.sp_list.push([p[1], p[0], p[2] || '', p[3] || '', p[4] || '']); } return sidx[p[1]]; };
  // cl254 = Watsonian vice counties (GB); cl133 = Irish vice counties (we keep the six in Northern Ireland)
  const top = await get(BASE + '&facets=cl254&facets=cl133&facets=license&facets=species_group&flimit=-1');
  out.totals = { records: top.totalRecords, cl254: fr(top, 'cl254').map(y => [y.label, y.count]), cl133: fr(top, 'cl133').map(y => [y.label, y.count]), license: fr(top, 'license').map(y => [y.label, y.count]), species_group: fr(top, 'species_group').map(y => [y.label, y.count]) };
  const vcs = [...out.totals.cl254.map(x => ['cl254', x[0]]), ...out.totals.cl133.filter(x => /^H(33|36|37|38|39|40) /.test(x[0])).map(x => ['cl133', x[0]])];
  for (const [fld, name] of vcs) {   // one facet query per vice county: every species and its record count
    const j = await get(BASE + '&fq=' + enc(fld + ':"' + name + '"') + '&facets=names_and_lsid&facets=data_resource_uid&facets=species_group&flimit=-1');
    const dr = fr(j, 'data_resource_uid').sort((a, b) => b.count - a.count);
    out.vc[name] = { field: fld, total: j.totalRecords, sp: fr(j, 'names_and_lsid').map(y => [addSp(y.label), y.count]).flat(), n_datasets: dr.length, top_datasets: dr.slice(0, 8).map(y => [y.label, y.count]), groups: fr(j, 'species_group').map(y => [y.label, y.count]) };
    await sleep(400);
  }
  for (const g of ['Birds', 'Mammals', 'Amphibians', 'Reptiles', 'FloweringPlants', 'Fishes', 'Insects', 'Bryophytes', 'Fungi', 'Molluscs', 'FernsAndAllies', 'SpidersAndAllies', 'Crustaceans', 'GymnospermsAndGinkgo', 'Algae', 'Plants', 'Animals'])
    out.groups[g] = fr(await get(BASE + '&fq=' + enc('species_group:' + g) + '&facets=taxon_concept_lsid&flimit=-1'), 'taxon_concept_lsid').map(y => y.label);
  for (const g of ['Butterflies and moths', 'Dragonflies', 'Beetles', 'Bats', 'Sawflies, wasps, bees and ants', 'True flies', 'Grasshoppers and crickets', 'Carnivores', 'Rodents', 'Perching birds', 'Ducks, geese and swans', 'Sandpipers, plovers, gulls and auks'])
    out.subgroups[g] = fr(await get(BASE + '&fq=' + enc('species_subgroup:"' + g + '"') + '&facets=taxon_concept_lsid&flimit=-1'), 'taxon_concept_lsid').map(y => y.label);
  // newcomers: vice counties with records in each period (all ranks, present, open licences)
  const LB = LIC + '&fq=' + enc('occurrence_status:PRESENT'), P = [[1970, 1989], [1990, 1999], [2000, 2009], [2010, 2019], [2020, 2026]];
  const INV = ['Sciurus carolinensis', 'Sciurus vulgaris', 'Harmonia axyridis', 'Psittacula krameri', 'Impatiens glandulifera', 'Reynoutria japonica', 'Pacifastacus leniusculus', 'Neovison vison', 'Muntiacus reevesi', 'Crassula helmsii', 'Alopochen aegyptiaca', 'Bombus hypnorum', 'Egretta garzetta', 'Rhododendron ponticum', 'Cameraria ohridella', 'Cettia cetti', 'Aricia agestis', 'Anax imperator', 'Erythromma viridulum', 'Lasius neglectus'];
  for (const s of INV) { out.invasive[s] = {}; for (const [a, b] of P) { const j = await get(LB + '&fq=' + enc('taxon_name:"' + s + '"') + '&fq=' + enc('year:[' + a + ' TO ' + b + ']') + '&facets=cl254&facets=cl133&flimit=-1'); out.invasive[s][a + '-' + b] = { total: j.totalRecords, cl254: fr(j, 'cl254').map(y => [y.label, y.count]), cl133: fr(j, 'cl133').map(y => [y.label, y.count]) }; await sleep(400); } }
  out.period_totals = {};
  for (const [a, b] of P) { const j = await get(LB + '&fq=' + enc('year:[' + a + ' TO ' + b + ']') + '&facets=cl254&flimit=-1'); out.period_totals[a + '-' + b] = { total: j.totalRecords, n_cl254: fr(j, 'cl254').length }; }
  const blob = await new Response(new Blob([JSON.stringify(out)]).stream().pipeThrough(new CompressionStream('gzip'))).blob();
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'cw_nbn_vc_2026.json.gz'; a.textContent = 'Download'; document.body.appendChild(a);
})();
