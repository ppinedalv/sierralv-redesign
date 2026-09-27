// SierraLV — nav, reveal, contact form
(() => {
  document.documentElement.classList.remove('no-js');

  // Mobile nav
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.getElementById('site-nav');
  const header = document.querySelector('.site-header');
  const setNavTop = () => {
    const r = header.getBoundingClientRect();
    document.documentElement.style.setProperty('--nav-top', `${Math.max(r.bottom, 0)}px`);
  };
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      setNavTop();
      toggle.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
      document.body.style.overflow = open && window.innerWidth < 1080 ? 'hidden' : '';
    });
  }

  // Dropdowns (click on all sizes, hover on desktop)
  const items = [...document.querySelectorAll('.nav__item[data-dropdown]')];
  const closeAll = (except) => items.forEach((it) => {
    if (it === except) return;
    it.classList.remove('is-open');
    it.querySelector('button')?.setAttribute('aria-expanded', 'false');
    if (window.innerWidth < 1080) it.querySelector('.nav__sub').hidden = true;
  });
  const syncSubs = () => items.forEach((it) => {
    const sub = it.querySelector('.nav__sub');
    sub.hidden = window.innerWidth < 1080 && !it.classList.contains('is-open');
  });
  syncSubs();
  window.addEventListener('resize', syncSubs);
  items.forEach((it) => {
    const btn = it.querySelector('button');
    const sub = it.querySelector('.nav__sub');
    btn.addEventListener('click', () => {
      const open = !it.classList.contains('is-open');
      closeAll(it);
      it.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', String(open));
      if (window.innerWidth < 1080) sub.hidden = !open;
    });
    it.addEventListener('mouseenter', () => { if (window.matchMedia('(hover: hover) and (min-width: 1080px)').matches) { closeAll(it); it.classList.add('is-open'); btn.setAttribute('aria-expanded', 'true'); } });
    it.addEventListener('mouseleave', () => { if (window.matchMedia('(hover: hover) and (min-width: 1080px)').matches) { it.classList.remove('is-open'); btn.setAttribute('aria-expanded', 'false'); } });
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeAll(); });
  document.addEventListener('click', (e) => { if (!e.target.closest('.nav__item[data-dropdown]') && window.innerWidth >= 1080) closeAll(); });

  // Reveal on scroll
  const els = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    els.forEach((el) => io.observe(el));
  } else {
    els.forEach((el) => el.classList.add('is-in'));
  }

  // Forms: compose an email to the office (static site, no backend)
  document.querySelectorAll('form[data-mailto]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      const data = new FormData(form);
      const lines = [];
      for (const [k, v] of data.entries()) if (v && k !== 'consent') lines.push(`${k}: ${v}`);
      const subject = encodeURIComponent(form.dataset.subject || 'Website inquiry');
      const body = encodeURIComponent(lines.join('\n'));
      window.location.href = `mailto:${form.dataset.mailto}?subject=${subject}&body=${body}`;
      const status = form.querySelector('.form__status');
      if (status) status.textContent = 'Opening your email app… If nothing happens, call us at 702-553-1211.';
    });
  });

  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();
