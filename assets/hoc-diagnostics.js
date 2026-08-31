(() => {
  const params = new URLSearchParams(window.location.search);
  if (params.get('hocdiag') !== '1') return;
  const build = document.querySelector('meta[name="hoc-build"]')?.content || 'missing';
  const vv = window.visualViewport;
  const facts = [['Build', build],['CSS viewport', `${window.innerWidth} × ${window.innerHeight}`],['Document client', `${document.documentElement.clientWidth} × ${document.documentElement.clientHeight}`],['Visual viewport', vv ? `${Math.round(vv.width)} × ${Math.round(vv.height)} @ ${vv.scale.toFixed(2)}` : 'unavailable'],['Screen', `${screen.width} × ${screen.height}`],['DPR', String(window.devicePixelRatio)],['Pointer coarse', String(matchMedia('(pointer:coarse)').matches)],['Pointer fine', String(matchMedia('(pointer:fine)').matches)],['Hover none', String(matchMedia('(hover:none)').matches)],['Reduced motion', String(matchMedia('(prefers-reduced-motion:reduce)').matches)],['Orientation', screen.orientation?.type || 'unavailable']];
  const panel = document.createElement('aside'); panel.id = 'hoc-diagnostic-panel'; panel.setAttribute('role', 'status'); panel.setAttribute('aria-label', 'House of Carol local diagnostic information');
  const heading = document.createElement('strong'); heading.textContent = 'HOC LOCAL DIAGNOSTIC — nothing is transmitted'; panel.append(heading);
  const list = document.createElement('dl'); for (const [key, value] of facts) { const term = document.createElement('dt'); term.textContent = key; const description = document.createElement('dd'); description.textContent = value; list.append(term, description); } panel.append(list); document.body.prepend(panel);
})();
