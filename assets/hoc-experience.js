(() => {
  const root = document.documentElement;
  root.classList.add('js');

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(pointer: fine)');
  const coarsePointer = window.matchMedia('(pointer: coarse)');
  const compactScreen = window.matchMedia('(max-width: 1024px)');

  const roomCopy = {
    business: ['Business & systems', 'Make the hard thing simpler.'],
    products: ['Products & tools', 'Useful beats impressive.'],
    publishing: ['Media & publishing', 'Make curiosity travel.'],
    other: ['Other ventures', 'Keep a room for the unexpected.']
  };

  const stage = document.querySelector('[data-house-stage]');
  const perspective = document.querySelector('[data-house-perspective]');
  const readout = document.querySelector('[data-house-readout]');
  const exterior = document.querySelector('[data-exterior]');
  let ambientTimers = [];

  const stopAmbient = () => {
    ambientTimers.forEach(window.clearTimeout);
    ambientTimers = [];
    document.querySelectorAll('[data-facade-room]').forEach((el) => el.classList.remove('is-ambient'));
  };

  if (stage && perspective) {
    const showRoom = (key) => {
      stopAmbient();
      stage.classList.add('has-room-focus');
      document.querySelectorAll('[data-facade-room]').forEach((el) => el.classList.toggle('is-active', el.dataset.facadeRoom === key));
      if (readout && roomCopy[key]) {
        readout.querySelector('span').textContent = roomCopy[key][0];
        readout.querySelector('strong').textContent = roomCopy[key][1];
      }
    };

    const clearRoom = () => {
      stage.classList.remove('has-room-focus');
      document.querySelectorAll('[data-facade-room]').forEach((el) => el.classList.remove('is-active'));
      if (readout) {
        readout.querySelector('span').textContent = 'House of Carol';
        readout.querySelector('strong').textContent = 'Move closer.';
      }
    };

    document.querySelectorAll('[data-room-hotspot]').forEach((link) => {
      const key = link.dataset.roomHotspot;
      link.addEventListener('mouseenter', () => showRoom(key));
      link.addEventListener('focus', () => showRoom(key));
      link.addEventListener('mouseleave', clearRoom);
      link.addEventListener('blur', clearRoom);
    });

    if (!reducedMotion.matches) {
      const rooms = [...document.querySelectorAll('[data-facade-room]')];
      rooms.forEach((room, index) => {
        ambientTimers.push(window.setTimeout(() => room.classList.add('is-ambient'), 650 + index * 170));
        ambientTimers.push(window.setTimeout(() => room.classList.remove('is-ambient'), 1600 + index * 210));
      });
    }

    if (!reducedMotion.matches && finePointer.matches && exterior) {
      exterior.addEventListener('pointermove', (event) => {
        const rect = exterior.getBoundingClientRect();
        const x = Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width));
        const y = Math.min(1, Math.max(0, (event.clientY - rect.top) / rect.height));
        exterior.style.setProperty('--mx', `${Math.round(x * 100)}%`);
        exterior.style.setProperty('--my', `${Math.round(y * 100)}%`);
        perspective.style.setProperty('--tilt-y', `${((x - 0.5) * 3.2).toFixed(2)}deg`);
        perspective.style.setProperty('--tilt-x', `${((0.5 - y) * 2.2).toFixed(2)}deg`);
      });
      exterior.addEventListener('pointerleave', () => {
        perspective.style.setProperty('--tilt-y', '0deg');
        perspective.style.setProperty('--tilt-x', '0deg');
      });
    }

    document.querySelectorAll('[data-enter-house]').forEach((link) => {
      const open = () => { stopAmbient(); stage.classList.add('is-door-open'); };
      const close = () => stage.classList.remove('is-door-open');
      link.addEventListener('mouseenter', open);
      link.addEventListener('focus', open);
      link.addEventListener('mouseleave', close);
      link.addEventListener('blur', close);
      link.addEventListener('click', (event) => {
        if (reducedMotion.matches || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button > 0) return;
        event.preventDefault();
        const destination = link.href;
        open();
        document.body.classList.add('is-entering');
        window.setTimeout(() => { window.location.href = destination; }, 360);
      });
    });
  }

  const planLinks = [...document.querySelectorAll('[data-plan-room]')];
  const indexLinks = [...document.querySelectorAll('[data-room-index]')];
  const panels = [...document.querySelectorAll('[data-room-panel]')];
  const planArts = [...document.querySelectorAll('[data-plan-art]')];
  const caption = document.querySelector('[data-plan-caption]');
  const roomDisplay = document.querySelector('.r10-room-display');
  const validRooms = new Set(Object.keys(roomCopy));

  const setRoom = (key, updateUrl = false) => {
    if (!validRooms.has(key)) return;
    planLinks.forEach((link) => {
      const active = link.dataset.planRoom === key;
      link.classList.toggle('is-current', active);
      if (active) link.setAttribute('aria-current', 'true'); else link.removeAttribute('aria-current');
    });
    indexLinks.forEach((link) => {
      const active = link.dataset.roomIndex === key;
      link.classList.toggle('is-current', active);
      if (active) link.setAttribute('aria-current', 'true'); else link.removeAttribute('aria-current');
    });
    planArts.forEach((art) => art.classList.toggle('is-current', art.dataset.planArt === key));
    panels.forEach((panel) => panel.classList.toggle('is-current', panel.dataset.roomPanel === key));
    document.body.dataset.roomTheme = key;
    if (caption) caption.textContent = `${roomCopy[key][0]} selected`;
    if (updateUrl) history.replaceState(null, '', `#${key}`);
  };

  const showSelectedRoomOnCompactExperience = () => {
    if ((!compactScreen.matches && !coarsePointer.matches) || !roomDisplay) return;
    roomDisplay.scrollIntoView({ behavior: reducedMotion.matches ? 'auto' : 'smooth', block: 'start' });
  };

  [...planLinks, ...indexLinks].forEach((link) => {
    link.addEventListener('click', (event) => {
      const key = link.dataset.planRoom || link.dataset.roomIndex;
      if (!validRooms.has(key)) return;
      event.preventDefault();
      setRoom(key, true);
      showSelectedRoomOnCompactExperience();
    });
  });

  if (panels.length) {
    const requested = location.hash.slice(1);
    setRoom(validRooms.has(requested) ? requested : 'business', false);
    window.addEventListener('hashchange', () => {
      const key = location.hash.slice(1);
      if (validRooms.has(key)) setRoom(key, false);
    });
  }

  // Local-only diagnostic mode. Nothing here is transmitted. It exists so a real
  // device can disprove our browser assumptions rather than forcing another guess.
  if (new URLSearchParams(location.search).get('hocdiag') === '1') {
    const build = document.querySelector('meta[name="hoc-build"]')?.content || 'missing';
    const vv = window.visualViewport;
    const facts = [
      ['Build', build],
      ['inner', `${window.innerWidth} × ${window.innerHeight}`],
      ['client', `${document.documentElement.clientWidth} × ${document.documentElement.clientHeight}`],
      ['visual', vv ? `${Math.round(vv.width)} × ${Math.round(vv.height)} @ ${vv.scale.toFixed(2)}` : 'unavailable'],
      ['screen', `${screen.width} × ${screen.height}`],
      ['DPR', String(window.devicePixelRatio)],
      ['coarse', String(coarsePointer.matches)],
      ['fine', String(finePointer.matches)],
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
    const heading = document.createElement('strong');
    heading.style.cssText = 'display:block;margin-bottom:5px;color:#f0d79f';
    heading.textContent = 'HOC LOCAL DIAGNOSTIC — nothing is transmitted';
    panel.append(heading);
    facts.forEach(([key, value]) => {
      const item = document.createElement('span');
      item.style.cssText = 'display:inline-block;margin:0 14px 3px 0';
      const label = document.createElement('b');
      label.textContent = `${key}: `;
      item.append(label, document.createTextNode(value));
      panel.append(item);
    });
    document.body.append(panel);
  }
})();
