(() => {
  const params = new URLSearchParams(location.search);
  if (params.get('hocdiag') !== '1') return;

  const build = document.querySelector('meta[name="hoc-build"]')?.content || 'missing';
  const vv = window.visualViewport;
  const facts = [
    ['Build', build],
    ['inner', `${window.innerWidth} × ${window.innerHeight}`],
    ['client', `${document.documentElement.clientWidth} × ${document.documentElement.clientHeight}`],
    ['visual', vv ? `${Math.round(vv.width)} × ${Math.round(vv.height)} @ ${vv.scale.toFixed(2)}` : 'unavailable'],
    ['screen', `${screen.width} × ${screen.height}`],
    ['DPR', String(window.devicePixelRatio)],
    ['coarse', String(matchMedia('(pointer:coarse)').matches)],
    ['fine', String(matchMedia('(pointer:fine)').matches)],
    ['hover-none', String(matchMedia('(hover:none)').matches)],
    ['orientation', screen.orientation?.type || 'unavailable']
  ];

  const panel = document.createElement('aside');
  panel.id = 'hoc-diagnostic-panel';
  panel.setAttribute('role', 'status');
  panel.setAttribute('aria-label', 'House of Carol local diagnostic information');
  panel.style.cssText = [
    'position:fixed','z-index:2147483647','left:8px','right:8px','bottom:8px',
    'padding:10px 12px','background:rgba(0,0,0,.94)','color:#fff','border:2px solid #f0d79f',
    'font:600 12px/1.45 ui-monospace,SFMono-Regular,Consolas,monospace','letter-spacing:0',
    'box-shadow:0 4px 20px rgba(0,0,0,.55)','max-height:42vh','overflow:auto'
  ].join(';');
  panel.innerHTML = '<strong style="display:block;margin-bottom:5px;color:#f0d79f">HOC LOCAL DIAGNOSTIC — nothing is transmitted</strong>' +
    facts.map(([k,v]) => `<span style="display:inline-block;margin:0 14px 3px 0"><b>${k}:</b> ${v}</span>`).join('');
  document.body.append(panel);
})();
