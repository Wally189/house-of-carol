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

  document.documentElement.classList.add('house-js');
  initWindow();
  initCounter();
  initWorkbench();
})();
