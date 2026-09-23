(function(){
  const W = window.WORK;
  if (!W) return;
  const esc = s => String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
  const body = document.getElementById('enbody');
  const pane = document.getElementById('enpane');

  /* ── 本文を組む ───────────────────────────── */
  let sentNo = 0;
  const sents = [];
  W.sections.forEach(sec => {
    const h = document.createElement('section');
    h.className = 'ensec';
    h.innerHTML = '<h2 class="ensec-head"><span class="num">' + esc(sec.n) + '</span>' +
                  esc(sec.title || ('Section ' + sec.n)) +
                  (sec.page ? '<span class="pg">' + esc(sec.page) + '</span>' : '') + '</h2>';
    (sec.lead || []).concat(sec.sents || []).forEach(st => {
      const i = sentNo++;
      sents.push(st);
      const chunks = st.en.split('/');
      const d = document.createElement('div');
      d.className = 'ensent';
      d.dataset.i = i;
      d.innerHTML =
        '<div class="enline">' + chunks.map((c, k) =>
          '<span class="chunk" data-k="' + k + '" tabindex="0" role="button">' +
          '<span class="cen">' + esc(c.trim()) + '</span>' +
          (st.parts && st.parts[k] ? '<span class="cja">' + esc(st.parts[k]) + '</span>' : '') +
          '</span>').join('<span class="slash" aria-hidden="true">/</span>') + '</div>' +
        '<div class="enja">' + esc(st.ja || '') + '</div>' +
        (st.sv ? '<div class="ensv"><b>骨組み</b>' + esc(st.sv) + '</div>' : '') +
        (st.n ? '<div class="ennote">' + st.n + '</div>' : '');
      h.appendChild(d);
    });
    body.appendChild(h);
  });

  /* ── 新出語 ───────────────────────────────── */
  const allWords = [];
  W.sections.forEach(sec => (sec.words || []).forEach(v => allWords.push(Object.assign({sec:sec.n}, v))));
  pane.innerHTML =
    '<div class="listhead">この課の新出語　全' + allWords.length + '語。' +
    '行をクリックすると本文中の語が光ります。</div>' +
    '<ul class="enwords">' + allWords.map((v, i) =>
      '<li><button data-w="' + esc(v.w) + '">' +
      '<span class="ww">' + esc(v.w) + '</span>' +
      '<span class="ipa">[' + esc(v.ipa) + ']</span>' +
      '<span class="pos">' + esc(v.pos) + '</span>' +
      '<span class="wm">' + esc(v.m) + '</span>' +
      '<span class="sec">' + esc(v.sec) + '</span>' +
      (v.n ? '<span class="wn">' + esc(v.n) + '</span>' : '') +
      '</button></li>').join('') + '</ul>';

  let lit = '';
  pane.addEventListener('click', e => {
    const b = e.target.closest('[data-w]'); if (!b) return;
    const w = b.dataset.w;
    pane.querySelectorAll('button.on').forEach(x => x.classList.remove('on'));
    body.querySelectorAll('mark.hit').forEach(m => m.replaceWith(...m.childNodes));
    if (lit === w) { lit = ''; return; }
    lit = w; b.classList.add('on');
    const re = new RegExp('\\b' + w.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&') + '\\w*', 'gi');
    let first = null;
    body.querySelectorAll('.cen').forEach(el => {
      if (!re.test(el.textContent)) return;
      re.lastIndex = 0;
      el.innerHTML = el.textContent.replace(re, m => '<mark class="hit">' + m + '</mark>');
      if (!first) first = el;
    });
    if (first) first.scrollIntoView({block:'center', behavior:'smooth'});
  });

  /* ── 表示の切り替え ───────────────────────── */
  const toggle = (id, attr, init) => {
    const b = document.getElementById(id); if (!b) return;
    let on = init;
    const apply = () => { b.setAttribute('aria-pressed', on); body.setAttribute(attr, on ? 'on' : 'off'); };
    b.onclick = () => { on = !on; apply(); };
    apply();
  };
  toggle('cjaBtn',   'data-cja',   false);   // 区切りごとの訳
  toggle('jaBtn',    'data-ja',    false);   // 全文訳
  toggle('noteBtn',  'data-note',  true);    // 構文メモ
  toggle('slashBtn', 'data-slash', true);    // 区切り線

  /* 区切りをクリックすると、その区切りの訳だけ出す */
  body.addEventListener('click', e => {
    const c = e.target.closest('.chunk'); if (!c) return;
    c.classList.toggle('open');
  });
  body.addEventListener('keydown', e => {
    const c = e.target.closest('.chunk'); if (!c) return;
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); c.classList.toggle('open'); }
  });

  document.getElementById('encount').textContent = sentNo + ' 文 / ' + allWords.length + ' 語';
})();
