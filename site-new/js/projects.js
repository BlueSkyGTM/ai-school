/* ============================================================
   AI SCHOOL · projects (capstone builds across all chapters)
   Shows ALL capstones — shipped ones open, locked ones with
   real content but a lock indicator. Sorted: shipped first.
   ============================================================ */
(async function () {
  'use strict';
  await window.AIS.store.init();
  const { store, ui } = window.AIS;
  const { el } = ui;
  const $ = (s) => document.querySelector(s);

  /* collect capstones from all chapters */
  const allCapstones = [];
  PHASES.forEach((ph) => {
    ph.lessons.forEach((l, i) => {
      if (
        l.type === 'Capstone' ||
        (l.url  && l.url.toLowerCase().includes('capstone')) ||
        (l.name && l.name.toLowerCase().includes('apstone'))
      ) {
        allCapstones.push({ ph, l, i, done: store.isDone(ph.id, i) });
      }
    });
  });

  /* shipped first, then by chapter */
  allCapstones.sort((a, b) => (b.done - a.done) || (a.ph.id - b.ph.id));

  const shippedCount = allCapstones.filter((c) => c.done).length;
  $('#capcount').textContent = shippedCount === 0
    ? `${allCapstones.length} builds · none shipped yet`
    : `${shippedCount} of ${allCapstones.length} shipped`;

  const tiles = allCapstones.map(({ ph, l, i, done }) => {
    const chTag  = `Ch. ${String(ph.id).padStart(2, '0')}`;
    const foot   = el('div', { class: 'proj__foot' }, [
      el('span', { class: 'proj__tag' }, chTag),
      done && l.url
        ? el('a',    { class: 'proj__link', href: l.url, target: '_blank', rel: 'noopener' }, 'View ↗')
        : done
          ? el('span', { class: 'proj__st is-shipped' }, 'Shipped')
          : el('a',    { class: 'proj__link proj__link--locked', href: 'course.html' }, '🔒 Complete in Course')
    ]);

    return el('div', { class: 'proj ' + (done ? 'is-shipped' : 'is-locked') }, [
      el('div', { class: 'proj__body' }, [
        el('div', { class: 'proj__name' }, l.name),
        el('div', { class: 'proj__desc' }, l.summary || ph.name),
        foot
      ])
    ]);
  });

  $('#builds').replaceChildren(...tiles);
})();
