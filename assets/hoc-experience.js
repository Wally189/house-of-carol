(() => {
  const root = document.documentElement;
  root.classList.add('js');

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(pointer: fine)');

  const roomNames = {
    business: 'Business & systems',
    products: 'Products & tools',
    publishing: 'Media & publishing',
    other: 'Other ventures'
  };

  const stage = document.querySelector('[data-house-stage]');
  const perspective = document.querySelector('[data-house-perspective]');
  const whisper = document.querySelector('[data-house-whisper]');

  if (stage && perspective) {
    const clearRoom = () => {
      stage.classList.remove('has-room-focus');
      document.querySelectorAll('[data-facade-room]').forEach((room) => room.classList.remove('is-active'));
      if (whisper) whisper.textContent = 'Move closer. The House will tell you what is here.';
    };

    const showRoom = (roomKey) => {
      stage.classList.add('has-room-focus');
      document.querySelectorAll('[data-facade-room]').forEach((room) => {
        room.classList.toggle('is-active', room.dataset.facadeRoom === roomKey);
      });
      if (whisper) whisper.textContent = `${roomNames[roomKey]}. Open the window to go straight there.`;
    };

    document.querySelectorAll('[data-room-hotspot]').forEach((hotspot) => {
      const roomKey = hotspot.dataset.roomHotspot;
      ['mouseenter', 'focus'].forEach((eventName) => hotspot.addEventListener(eventName, () => showRoom(roomKey)));
      ['mouseleave', 'blur'].forEach((eventName) => hotspot.addEventListener(eventName, clearRoom));
    });

    if (!reducedMotion.matches && finePointer.matches) {
      const arrival = document.querySelector('.arrival');
      arrival?.addEventListener('pointermove', (event) => {
        const rect = arrival.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width;
        const y = (event.clientY - rect.top) / rect.height;
        arrival.style.setProperty('--mx', `${Math.round(x * 100)}%`);
        arrival.style.setProperty('--my', `${Math.round(y * 100)}%`);
        perspective.style.setProperty('--tilt-y', `${((x - 0.5) * 5).toFixed(2)}deg`);
        perspective.style.setProperty('--tilt-x', `${((0.5 - y) * 3).toFixed(2)}deg`);
      });
      arrival?.addEventListener('pointerleave', () => {
        perspective.style.setProperty('--tilt-y', '0deg');
        perspective.style.setProperty('--tilt-x', '0deg');
      });
    }

    document.querySelectorAll('[data-enter-house]').forEach((link) => {
      link.addEventListener('mouseenter', () => stage.classList.add('is-door-open'));
      link.addEventListener('focus', () => stage.classList.add('is-door-open'));
      link.addEventListener('mouseleave', () => stage.classList.remove('is-door-open'));
      link.addEventListener('blur', () => stage.classList.remove('is-door-open'));
      link.addEventListener('click', (event) => {
        if (reducedMotion.matches || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button > 0) return;
        const destination = link.href;
        event.preventDefault();
        stage.classList.add('is-door-open');
        document.body.classList.add('is-entering');
        if (whisper) whisper.textContent = 'The door is open.';
        window.setTimeout(() => { window.location.href = destination; }, 520);
      });
    });
  }

  const theatre = document.querySelector('[data-plan-theatre]');
  const caption = document.querySelector('[data-plan-caption]');
  const planRooms = [...document.querySelectorAll('[data-plan-room]')];

  if (theatre && planRooms.length) {
    const planCopy = {
      business: 'Business & systems. Practical work that makes the complicated useful.',
      products: 'Products & tools. Things stay only when they are worth keeping.',
      publishing: 'Media & publishing. Curiosity, explanation and work worth returning to.',
      other: 'Other ventures. Space for the useful thing that refuses a familiar label.'
    };

    const setCurrent = (roomKey) => {
      planRooms.forEach((room) => room.classList.toggle('is-current', room.dataset.planRoom === roomKey));
      if (caption && planCopy[roomKey]) caption.textContent = planCopy[roomKey];
    };

    planRooms.forEach((room) => {
      const roomKey = room.dataset.planRoom;
      ['mouseenter', 'focus'].forEach((eventName) => room.addEventListener(eventName, () => setCurrent(roomKey)));
    });

    if (!reducedMotion.matches && finePointer.matches) {
      theatre.addEventListener('pointermove', (event) => {
        const rect = theatre.getBoundingClientRect();
        theatre.style.setProperty('--plan-x', `${Math.round(((event.clientX - rect.left) / rect.width) * 100)}%`);
        theatre.style.setProperty('--plan-y', `${Math.round(((event.clientY - rect.top) / rect.height) * 100)}%`);
      });
    }

    const chapters = [...document.querySelectorAll('[data-room-chapter]')];
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            const roomKey = entry.target.dataset.roomChapter;
            if (roomKey) setCurrent(roomKey);
          }
        });
      }, { threshold: 0.35 });
      chapters.forEach((chapter) => observer.observe(chapter));
    } else {
      chapters.forEach((chapter) => chapter.classList.add('is-visible'));
    }
  }
})();
