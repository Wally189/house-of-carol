(() => {
  'use strict';

  const windowItems = [
    {
      eyebrow: 'IN THE WINDOW · KEY-PERSON RISK',
      title: 'The employee who remembers everything is doing two jobs.',
      body: 'One job is the work you hired them for. The other is being the undocumented operating system. Growth, holiday or illness eventually sends you the invoice.',
      link: '#counter',
      linkText: 'Check where your process depends on memory'
    },
    {
      eyebrow: 'IN THE WINDOW · DIGITAL',
      title: 'Before automating a spreadsheet, ask why the spreadsheet exists.',
      body: 'Sometimes the clever automation is to stop entering the same information twice. The House starts with the reason for the work, not the most fashionable tool for doing it.',
      link: '#repairs',
      linkText: 'See how the repair menu works'
    },
    {
      eyebrow: 'IN THE WINDOW · CUSTOMER EXPERIENCE',
      title: 'A customer should not need your organisation chart to buy from you.',
      body: 'If people have to understand which inbox, form, team or person owns the next step, the internal structure has leaked into the service. That is repairable.',
      link: '#workbench',
      linkText: 'Open the Workbench'
    },
    {
      eyebrow: 'IN THE WINDOW · SMALL NUMBERS',
      title: 'The irritating fifteen-minute job may be bigger than it looks.',
      body: 'Repeated work hides in small units. A job that only takes minutes can quietly absorb days across a year. Measure the repetition before deciding whether it deserves a repair.',
      link: '#cabinet',
      linkText: 'Open the Cabinet and count it'
    },
    {
      eyebrow: 'IN THE WINDOW · GROWTH',
      title: 'The old way can be perfectly sensible and still be finished.',
      body: 'A process that worked for twenty customers can become ridiculous at two hundred. Outgrowing a method is evidence of change, not incompetence.',
      link: '#counter',
      linkText: 'Bring the symptom to the Counter'
    }
  ];

  const symptomMap = {
    chase: {
      label: 'We keep chasing',
      inspect: 'ownership, waiting points, triggers, approvals and whether the next action is visible without another email',
      lane: 'process'
    },
    retype: {
      label: 'We type the same thing again',
      inspect: 'duplicate records, hand-offs, authoritative sources and what can be captured once instead of reconstructed',
      lane: 'process'
    },
    memory: {
      label: 'One person remembers everything',
      inspect: 'exceptions, undocumented decisions, key-person dependency and what needs to become visible without turning into bureaucracy',
      lane: 'process'
    },
    website: {
      label: 'The website does not feel like us',
      inspect: 'customer intent, hierarchy, content, trust, navigation, accessibility, conversion friction and whether the digital experience matches the real business',
      lane: 'whole'
    },
    customer: {
      label: 'Customers get lost',
      inspect: 'the end-to-end customer journey, hand-offs, messages, response points and places where your internal structure becomes their problem',
      lane: 'whole'
    },
    onboarding: {
      label: 'Onboarding is a scavenger hunt',
      inspect: 'inputs, roles, documents, sequence, missing information and which steps are genuinely necessary',
      lane: 'process'
    },
    reports: {
      label: 'Reporting eats the day',
      inspect: 'source data, repeated manipulation, ownership, frequency, decision value and whether the report still deserves to exist in its current form',
      lane: 'process'
    },
    tools: {
      label: 'We have too many tools',
      inspect: 'what each tool is actually for, overlap, subscriptions, data duplication, manual bridges and what can be retired before anything new is bought',
      lane: 'whole'
    },
    whole: {
      label: 'I cannot name it — the whole place feels harder',
      inspect: 'the business end to end: customer experience, operations, information, digital tools, website, controls and the points where several small irritations share one cause',
      lane: 'whole'
    }
  };

  function initWindow() {
    const panel = document.querySelector('[data-house-window]');
    if (!panel) return;
    const eyebrow = panel.querySelector('[data-window-eyebrow]');
    const title = panel.querySelector('[data-window-title]');
    const body = panel.querySelector('[data-window-body]');
    const link = panel.querySelector('[data-window-link]');
    const counter = panel.querySelector('[data-window-count]');
    const prev = panel.querySelector('[data-window-prev]');
    const next = panel.querySelector('[data-window-next]');
    let index = 0;

    function render() {
      const item = windowItems[index];
      eyebrow.textContent = item.eyebrow;
      title.textContent = item.title;
      body.textContent = item.body;
      link.href = item.link;
      link.textContent = item.linkText;
      counter.textContent = `${String(index + 1).padStart(2, '0')} / ${String(windowItems.length).padStart(2, '0')}`;
    }

    prev?.addEventListener('click', () => {
      index = (index - 1 + windowItems.length) % windowItems.length;
      render();
    });
    next?.addEventListener('click', () => {
      index = (index + 1) % windowItems.length;
      render();
    });
    render();
  }

  function initCounter() {
    const counter = document.querySelector('[data-counter]');
    if (!counter) return;
    const buttons = [...counter.querySelectorAll('[data-symptom]')];
    const result = counter.querySelector('[data-counter-result]');
    const heading = counter.querySelector('[data-counter-heading]');
    const copy = counter.querySelector('[data-counter-copy]');
    const list = counter.querySelector('[data-counter-list]');
    const route = counter.querySelector('[data-counter-route]');
    const reset = counter.querySelector('[data-counter-reset]');
    const selected = new Set();

    function render() {
      buttons.forEach((button) => {
        const active = selected.has(button.dataset.symptom);
        button.setAttribute('aria-pressed', active ? 'true' : 'false');
      });

      if (!selected.size) {
        heading.textContent = 'Pick the things that feel familiar.';
        copy.textContent = 'Nothing leaves this page. The Counter simply shows what the House would look at first.';
        list.innerHTML = '';
        route.textContent = 'No diagnosis yet — which is exactly how a counter should behave before you tell it anything.';
        result.dataset.state = 'empty';
        return;
      }

      const items = [...selected].map((key) => symptomMap[key]);
      const wholeCount = items.filter((item) => item.lane === 'whole').length;
      const broad = selected.has('whole') || wholeCount >= 2 || selected.size >= 4;

      heading.textContent = broad ? 'This looks connected, not isolated.' : 'There is a sensible first place to look.';
      copy.textContent = broad
        ? 'Several symptoms are touching different parts of the business. The useful question is whether one root cause is creating several local workarounds.'
        : 'The irritation is narrow enough to trace without turning the whole company upside down.';

      list.innerHTML = '';
      items.forEach((item) => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${item.label}:</strong> we would inspect ${item.inspect}.`;
        list.appendChild(li);
      });

      route.innerHTML = broad
        ? '<strong>Likely starting route:</strong> a Full House Review or a deliberately bounded multi-area review — priced only after the boundary is clear.'
        : '<strong>Likely starting route:</strong> the £149 One-Process Rescue. If the diagnosis shows the issue is broader, we say so before enlarging the job.';
      result.dataset.state = 'ready';
    }

    buttons.forEach((button) => {
      button.addEventListener('click', () => {
        const key = button.dataset.symptom;
        if (selected.has(key)) selected.delete(key);
        else selected.add(key);
        render();
      });
    });

    reset?.addEventListener('click', () => {
      selected.clear();
      render();
      buttons[0]?.focus();
    });

    render();
  }

  function initWorkbench() {
    const bench = document.querySelector('[data-workbench]');
    if (!bench) return;
    const tabs = [...bench.querySelectorAll('[data-bench-tab]')];
    const panels = [...bench.querySelectorAll('[data-bench-panel]')];

    function show(name, focus = false) {
      tabs.forEach((tab) => {
        const active = tab.dataset.benchTab === name;
        tab.setAttribute('aria-selected', active ? 'true' : 'false');
        tab.tabIndex = active ? 0 : -1;
        if (active && focus) tab.focus();
      });
      panels.forEach((panel) => {
        const active = panel.dataset.benchPanel === name;
        panel.hidden = !active;
      });
    }

    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => show(tab.dataset.benchTab));
      tab.addEventListener('keydown', (event) => {
        if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
        event.preventDefault();
        const delta = event.key === 'ArrowRight' ? 1 : -1;
        const nextIndex = (index + delta + tabs.length) % tabs.length;
        show(tabs[nextIndex].dataset.benchTab, true);
      });
    });

    show(tabs.find((tab) => tab.getAttribute('aria-selected') === 'true')?.dataset.benchTab || tabs[0]?.dataset.benchTab);
  }

  function initCabinet() {
    const anchor = document.querySelector('.notes-section');
    if (!anchor || document.getElementById('cabinet')) return;

    const style = document.createElement('style');
    style.textContent = `
      .cabinet-section{padding:6.5rem 0;background:#0d315a;color:#fff;border-top:2px solid #14171a;border-bottom:2px solid #14171a}
      .cabinet-section h2,.cabinet-section h3{color:#fff}.cabinet-section .kicker{color:#bdd8ef}
      .cabinet-intro{display:grid;grid-template-columns:.8fr 1.2fr;gap:4rem;align-items:end;margin-bottom:2.6rem}
      .cabinet-intro>p{max-width:58ch;color:#dce9f4;border-left:7px solid #4f8fca;padding-left:1.3rem}
      .cabinet-drawer{display:grid;grid-template-columns:minmax(0,.92fr) minmax(340px,1.08fr);border:2px solid #fff;background:#f4efe5;color:#14171a;box-shadow:15px 17px 0 rgba(0,0,0,.18)}
      .cabinet-form{padding:2.2rem;border-right:2px solid #14171a}
      .cabinet-cap{display:flex;justify-content:space-between;gap:1rem;border-bottom:1px solid #b8b0a4;padding-bottom:1rem;margin-bottom:1.4rem;font-size:.7rem;text-transform:uppercase;font-weight:900;letter-spacing:.16em}
      .cabinet-fields{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
      .cabinet-field label{display:block;font-weight:800;margin-bottom:.4rem}.cabinet-field small{display:block;color:#626b74;margin-top:.35rem;line-height:1.35}
      .cabinet-field input{width:100%;border:1.5px solid #14171a;background:#fffdf7;color:#14171a;font:inherit;padding:.78rem .8rem;border-radius:0}
      .cabinet-field input:focus{outline:3px solid #4f8fca;outline-offset:2px}
      .cabinet-result{padding:2.7rem 3rem;background:linear-gradient(135deg,#fffdf7 0 77%,#d9eaf7 77% 100%);display:flex;flex-direction:column;justify-content:center}
      .cabinet-result .result-label{font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;font-weight:900;color:#235f9f}
      .cabinet-result output{display:block;font:500 clamp(3rem,7vw,6.5rem)/.9 Georgia,"Times New Roman",serif;color:#0d315a;margin:.7rem 0}
      .cabinet-result h3{color:#14171a;font:500 clamp(1.6rem,3vw,2.6rem)/1.05 Georgia,"Times New Roman",serif;max-width:17ch;margin:.4rem 0 1rem}
      .cabinet-result p{color:#414950;max-width:58ch}.cabinet-result .cabinet-money{font-weight:900;color:#0d315a}
      .cabinet-note{font-size:.78rem!important;color:#626b74!important;border-top:1px solid #b8b0a4;padding-top:1rem;margin-top:1.4rem!important}
      @media(max-width:900px){.cabinet-intro,.cabinet-drawer{grid-template-columns:1fr}.cabinet-intro{gap:1.4rem}.cabinet-form{border-right:0;border-bottom:2px solid #14171a}.cabinet-fields{grid-template-columns:1fr 1fr}}
      @media(max-width:580px){.cabinet-section{padding:4.6rem 0}.cabinet-fields{grid-template-columns:1fr}.cabinet-form,.cabinet-result{padding:1.6rem}.cabinet-result output{font-size:3.5rem}}
    `;
    document.head.appendChild(style);

    const section = document.createElement('section');
    section.id = 'cabinet';
    section.className = 'cabinet-section';
    section.setAttribute('aria-labelledby', 'cabinet-title');
    section.innerHTML = `
      <div class="shell">
        <div class="cabinet-intro">
          <div><p class="kicker">The Cabinet · Tool 001</p><h2 id="cabinet-title">How big is the tiny irritating job?</h2></div>
          <p>Repeated admin hides because each occurrence looks harmless. Put in rough numbers and the Cabinet will show the annual time footprint. Nothing is sent, stored or used to sell to you.</p>
        </div>
        <div class="cabinet-drawer" data-friction-calc>
          <form class="cabinet-form" onsubmit="return false">
            <div class="cabinet-cap"><span>Friction counter</span><span>Runs in this browser only</span></div>
            <div class="cabinet-fields">
              <div class="cabinet-field"><label for="cab-minutes">Minutes each time</label><input id="cab-minutes" name="minutes" type="number" min="0" max="1440" step="1" value="15" inputmode="decimal"><small>How long one occurrence actually takes.</small></div>
              <div class="cabinet-field"><label for="cab-times">Times each week</label><input id="cab-times" name="times" type="number" min="0" max="500" step="1" value="5" inputmode="decimal"><small>Across the whole process, not just one person.</small></div>
              <div class="cabinet-field"><label for="cab-people">People involved</label><input id="cab-people" name="people" type="number" min="1" max="500" step="1" value="1" inputmode="decimal"><small>Use 1 if the weekly count already includes everyone.</small></div>
              <div class="cabinet-field"><label for="cab-weeks">Working weeks</label><input id="cab-weeks" name="weeks" type="number" min="1" max="52" step="1" value="47" inputmode="decimal"><small>Adjust for seasonality, closures or holidays.</small></div>
              <div class="cabinet-field"><label for="cab-hourly">Optional £ value per hour</label><input id="cab-hourly" name="hourly" type="number" min="0" max="10000" step="1" value="0" inputmode="decimal"><small>Only if an indicative internal time value is useful to you.</small></div>
            </div>
          </form>
          <div class="cabinet-result" aria-live="polite">
            <span class="result-label">Annual time footprint</span>
            <output data-friction-hours>58.8 hours</output>
            <h3 data-friction-plain>Nearly eight working days spent on one small repeated job.</h3>
            <p data-friction-money class="cabinet-money"></p>
            <p class="cabinet-note">This is arithmetic from your assumptions, not a promised saving. Some of the time may be necessary control. The House would ask what can disappear, what must remain and whether changing it is worth the disruption.</p>
          </div>
        </div>
      </div>`;
    anchor.parentNode.insertBefore(section, anchor);

    const form = section.querySelector('[data-friction-calc]');
    const inputs = [...form.querySelectorAll('input')];
    const hoursOut = form.querySelector('[data-friction-hours]');
    const plainOut = form.querySelector('[data-friction-plain]');
    const moneyOut = form.querySelector('[data-friction-money]');

    function n(name) {
      const value = Number(form.querySelector(`[name="${name}"]`)?.value || 0);
      return Number.isFinite(value) && value >= 0 ? value : 0;
    }

    function render() {
      const minutes = n('minutes');
      const times = n('times');
      const people = Math.max(1, n('people'));
      const weeks = Math.max(1, n('weeks'));
      const hourly = n('hourly');
      const hours = (minutes * times * people * weeks) / 60;
      const days = hours / 7.5;
      hoursOut.textContent = `${hours.toLocaleString('en-GB', {maximumFractionDigits:1})} hours`;
      if (hours < 1) plainOut.textContent = 'Small in annual terms — perhaps not worth redesigning unless it causes another problem.';
      else if (days < 1) plainOut.textContent = 'Less than a working day across the year. The annoyance may matter more than the time.';
      else if (days < 10) plainOut.textContent = `About ${days.toLocaleString('en-GB', {maximumFractionDigits:1})} working days across the year.`;
      else plainOut.textContent = `About ${days.toLocaleString('en-GB', {maximumFractionDigits:0})} working days across the year — enough to deserve a proper look.`;
      moneyOut.textContent = hourly > 0 ? `At £${hourly.toLocaleString('en-GB', {maximumFractionDigits:0})}/hour, that is about £${(hours * hourly).toLocaleString('en-GB', {maximumFractionDigits:0})} of time.` : '';
    }

    inputs.forEach((input) => input.addEventListener('input', render));
    render();
  }

  document.documentElement.classList.add('house-js');
  initWindow();
  initCounter();
  initWorkbench();
  initCabinet();
})();