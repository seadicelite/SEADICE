// 研究で確かめられた尺度（○件法・下位尺度の合計点）用の診断エンジン
(function(){
  var dataEl = document.getElementById('scale-data');
  if (!dataEl) return;
  var data = JSON.parse(dataEl.textContent);
  var listEl = document.getElementById('quiz-questions');
  var resultEl = document.getElementById('quiz-result');
  var progressBar = document.getElementById('quiz-progress-bar');
  var progressLabel = document.getElementById('quiz-progress-label');
  var progressWrap = document.getElementById('quiz-progress-wrap');
  var introEl = document.getElementById('quiz-intro');
  var startBtn = document.getElementById('quiz-start-btn');

  var total = data.items.length;
  var points = data.labels.length;
  var answers = new Array(total).fill(null);
  var current = 0;

  var PROFILE_KEY = 'seadice_diag_profile_v1';
  var slug = location.pathname.replace(/^\/diagnosis\//, '').replace(/\/.*$/, '');
  function loadProfile(){
    try { return JSON.parse(localStorage.getItem(PROFILE_KEY)) || {}; } catch (e) { return {}; }
  }

  function renderQuestion(){
    progressBar.style.width = (current / total * 100) + '%';
    progressLabel.textContent = (current + 1) + ' / ' + total;
    listEl.innerHTML = '';
    var block = document.createElement('div');
    block.className = 'q-block';
    var lead = document.createElement('p');
    lead.className = 'q-lead';
    lead.textContent = pickLabel ? data.pick.lead.replace('{label}', pickLabel) : data.lead;
    block.appendChild(lead);
    var title = document.createElement('p');
    title.className = 'q-title';
    title.innerHTML = '<span class="q-num">Q' + (current + 1) + '</span>' + data.items[current].text;
    block.appendChild(title);
    var optList = document.createElement('div');
    optList.className = 'q-opt-list';
    data.labels.forEach(function(label, i){
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'q-opt' + (answers[current] === i + 1 ? ' q-opt-on' : '');
      btn.innerHTML = '<span class="q-opt-dot"></span><span>' + label + '</span>';
      btn.addEventListener('click', function(){
        answers[current] = i + 1;
        if (current < total - 1) { current++; renderQuestion(); } else { showResult(); }
      });
      optList.appendChild(btn);
    });
    block.appendChild(optList);
    var back = document.createElement('button');
    back.type = 'button';
    back.className = 'q-back';
    back.textContent = '← 前の質問に戻る';
    back.disabled = current === 0;
    back.addEventListener('click', function(){ if (current > 0) { current--; renderQuestion(); } });
    block.appendChild(back);
    listEl.appendChild(block);
  }

  function levelOf(score, k){
    if (k.bands) {
      // 作者が示した点数の区分で判定する（高い区分から順に）
      for (var i = 0; i < k.bands.length; i++) {
        var b = k.bands[i];
        if (score >= b.min) return {id: b.level, label: b.label, z: score, band: b};
      }
    }
    var z = (score - k.mean) / k.sd;
    if (z >= 0.5) return {id: 'high', label: '高め', z: z};
    if (z <= -0.5) return {id: 'low', label: '低め', z: z};
    return {id: 'mid', label: 'ふつう', z: z};
  }

  // norms: くらべる相手（年代・性別など）を選べる尺度。groups["軸1|軸2"] = {特性: [平均, SD]}
  var NORM_KEY = 'seadice_diag_norm_v1';
  var HIST_KEY = 'seadice_diag_history_v1';
  var norms = data.norms, normSel = null, scores = null;
  // pick: 答える前に「誰について答えるか」などを選ぶ（norms の軸と連動。履歴も選んだもの別）
  var pickLabel = '';
  if (norms) {
    normSel = norms.default.split('|');
    try { var ns = (JSON.parse(localStorage.getItem(NORM_KEY)) || {})[slug]; if (ns && norms.groups[ns]) normSel = ns.split('|'); } catch (e) {}
  }
  function normGroup(){
    var g = norms.groups[normSel.join('|')];
    var fb = !g;
    if (fb) g = norms.groups[normSel[0] + '|' + norms.axes[1].options[0][0]];
    return {g: g, fallback: fb};
  }
  function labelOf(ax, id){
    var o = norms.axes[ax].options.filter(function(x){ return x[0] === id; })[0];
    return o ? o[1] : '';
  }
  // 正規分布で「100人中、自分より高い人の数」の目安を出す
  function above100(z){
    var t = 1 / (1 + 0.3275911 * Math.abs(z) / Math.SQRT2);
    var erf = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-z * z / 2);
    var cdf = 0.5 * (1 + (z >= 0 ? erf : -erf));
    return Math.min(99, Math.max(1, Math.round((1 - cdf) * 100)));
  }
  // 端末の日付（toISOString はUTCなので日本の朝に前日になる）
  function today(){
    var d = new Date();
    return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
  }
  function loadHist(){
    try { return JSON.parse(localStorage.getItem(HIST_KEY)) || {}; } catch (e) { return {}; }
  }

  function sumOf(sc){ return Object.keys(data.keys).reduce(function(t, k){ return t + (sc[k] || 0); }, 0); }

  function showResult(){
    var keys = Object.keys(data.keys);
    scores = {};
    keys.forEach(function(k){ scores[k] = 0; });
    data.items.forEach(function(it, i){
      var v = answers[i];
      scores[it.key] += it.reverse ? (points + 1 - v) : v;
    });

    // 前回の結果（端末内の履歴）とくらべてから、今回を足す
    var prevScores = null, prevAt = '';
    try {
      var hk = slug + (pickLabel ? '|' + normSel[data.pick.axis] : '');
      var h = loadHist(), list = h[hk] || [];
      if (list.length) { prevScores = list[list.length - 1].scores; prevAt = list[list.length - 1].at; }
      list.push({at: today(), scores: scores});
      h[hk] = list.slice(-20);
      localStorage.setItem(HIST_KEY, JSON.stringify(h));
    } catch (e) {}
    var diffEl = resultEl.querySelector('.sc-diff');
    if (!diffEl) {
      diffEl = document.createElement('p');
      diffEl.className = 'sc-diff';
      resultEl.querySelector('.sc-list').insertAdjacentElement('afterend', diffEl);
    }
    if (prevScores) {
      var fmt = function(d){ return d > 0 ? '+' + d : d < 0 ? '−' + (-d) : '±0'; };
      // total: 合計の差と、変わった項目だけを出す（項目が多い診断で長くならないように）
      var dk = keys.filter(function(k){ return prevScores[k] != null && (!data.total || scores[k] !== prevScores[k]); });
      var parts = dk.map(function(k){ return data.keys[k].name + ' ' + fmt(scores[k] - prevScores[k]); });
      if (data.total) parts.unshift(data.total.name + ' ' + fmt(sumOf(scores) - sumOf(prevScores)));
      diffEl.innerHTML = '<b>前回（' + prevAt + '）とくらべて</b>' + parts.join('、');
      diffEl.style.display = '';
    } else diffEl.style.display = 'none';

    progressWrap.style.display = 'none';
    listEl.style.display = 'none';
    resultEl.style.display = 'block';
    if (norms) renderNormPicker();
    render();
    window.scrollTo({top: 0, behavior: 'smooth'});
  }

  function renderNormPicker(){
    var box = resultEl.querySelector('.norm-pick');
    if (!box) {
      box = document.createElement('div');
      box.className = 'norm-pick';
      var note = resultEl.querySelector('.sc-note');
      note.parentNode.insertBefore(box, note);
    }
    box.innerHTML = '<p class="norm-title">くらべる相手</p>' + norms.axes.map(function(ax, ai){
      if (data.pick && ai === data.pick.axis) return '';
      return '<div class="norm-row" role="group" aria-label="' + ax.label + '"><span class="norm-ax">' + ax.label + '</span>' + ax.options.map(function(o){
        return '<button type="button" class="norm-chip" data-ax="' + ai + '" data-id="' + o[0] + '" aria-pressed="' + (normSel[ai] === o[0]) + '">' + o[1] + '</button>';
      }).join('') + '</div>';
    }).join('');
    box.querySelectorAll('.norm-chip').forEach(function(btn){
      btn.addEventListener('click', function(){
        normSel[+btn.dataset.ax] = btn.dataset.id;
        try { var m = JSON.parse(localStorage.getItem(NORM_KEY)) || {}; m[slug] = normSel.join('|'); localStorage.setItem(NORM_KEY, JSON.stringify(m)); } catch (e) {}
        renderNormPicker();
        render();
      });
    });
  }

  function render(){
    var keys = Object.keys(data.keys);
    var ng = norms ? normGroup() : null;
    var html = '';
    var tori = [];
    var top = null;
    // sortByScore: 点数の高い順に並べる（同点はもとの順）
    if (data.sortByScore) keys = keys.map(function(k, i){ return [k, i]; }).sort(function(x, y){ return scores[y[0]] - scores[x[0]] || x[1] - y[1]; }).map(function(x){ return x[0]; });
    keys.forEach(function(k){
      var d = data.keys[k], s = scores[k];
      if (ng) d = Object.assign({}, d, {mean: ng.g[k][0], sd: ng.g[k][1]});
      var lv = levelOf(s, d), t = lv.band || d[lv.id];
      if (!top || lv.z > top.z) top = {k: k, z: lv.z, lv: lv};
      var pos = (s - d.min) / (d.max - d.min) * 100;
      var mean = d.mean != null ? (d.mean - d.min) / (d.max - d.min) * 100 : null;
      var pct = data.percentile && d.sd ? '<p class="sc-pct">100人いたら、あなたより高い人はおよそ' + above100(lv.z) + '人</p>' : '';
      html += '<div class="sc-item sc-' + lv.id + '">' +
        '<p class="sc-head"><span class="sc-name">' + d.name + '</span><span class="sc-level">' + lv.label + '（' + s + '点）</span></p>' +
        '<div class="sc-bar" role="img" aria-label="' + d.name + ' ' + s + '点（' + d.min + '〜' + d.max + '点' + (mean != null ? '、平均' + d.mean + '点' : '') + '）"><i style="width:' + pos + '%"></i>' + (mean != null ? '<b style="left:' + mean + '%"></b>' : '') + '</div>' +
        pct + '<p class="sc-desc">' + t.desc + '</p></div>';
      if (t.tori) tori.push(t.tori);
    });

    if (ng && norms.who) {
      resultEl.querySelector('.sc-note').textContent = 'バーの縦線は' + norms.who.replace('{0}', labelOf(0, normSel[0])).replace('{1}', labelOf(1, normSel[1])) + 'です。';
    } else if (ng) {
      var who = normSel[0] === norms.studentId ? norms.studentLabel : labelOf(0, normSel[0]) + (ng.fallback || normSel[1] === norms.axes[1].options[0][0] ? '' : 'の' + labelOf(1, normSel[1])) + 'の平均（' + norms.adultSource + '）';
      resultEl.querySelector('.sc-note').textContent = '各' + data.keys[Object.keys(data.keys)[0]].min + '〜' + data.keys[Object.keys(data.keys)[0]].max + '点。バーの縦線は' + who + 'です。' + (ng.fallback ? '大学生は男女別の平均がないため、男女あわせた平均とくらべています。' : '');
    }
    resultEl.querySelector('.sc-list').innerHTML = html;
    resultEl.querySelector('.tori-list').innerHTML = tori.map(function(t){ return '<li>' + t + '</li>'; }).join('');
    var toriBox = resultEl.querySelector('.tori');
    if (toriBox) toriBox.style.display = tori.length ? '' : 'none';

    var summary = data.summary(top, data.keys);
    var color = data.keys[top.k].color;
    // total: 全項目の合計点を bands で1つの段階に分け、結果のいちばん上に出す
    var tb = data.total && resultEl.querySelector('.total-box');
    if (tb) {
      var tot = sumOf(scores), tl = levelOf(tot, data.total), band = tl.band;
      tb.innerHTML = '<p class="total-name">' + band.label + '</p>' +
        '<p class="total-score">' + data.total.name + ' ' + tot + '点（' + data.total.min + '〜' + data.total.max + '点）</p>' +
        '<p class="total-desc">' + band.desc + '</p>';
      summary = data.total.name + '：' + band.label;
      if (band.color) color = band.color;
    }
    // quadrant: 2つの尺度の高低で4つの型に分ける（区切りは cut × 項目数）
    var q = data.quadrant;
    if (q) {
      var xs = scores[q.x], ys = scores[q.y], kx = data.keys[q.x], ky = data.keys[q.y];
      var cx = q.cut * kx.min, cy = q.cut * ky.min;
      var t = q.types[(ys > cy ? '1' : '0') + (xs > cx ? '1' : '0')];
      summary = t.name + (pickLabel ? '（' + pickLabel + '）' : '');
      color = t.color;
      var px = (xs - kx.min) / (kx.max - kx.min) * 100, py = (ys - ky.min) / (ky.max - ky.min) * 100;
      var mx = (cx - kx.min) / (kx.max - kx.min) * 100, my = (cy - ky.min) / (ky.max - ky.min) * 100;
      resultEl.querySelector('.quad').innerHTML = '<p class="quad-name" style="color:' + t.color + '">' + t.name + '</p><p class="quad-desc">' + t.desc + '</p>' +
        '<p class="quad-ylab">↑ ' + ky.name + ' 高い</p><div class="quad-map" role="img" aria-label="' + kx.name + ' ' + xs + '点、' + ky.name + ' ' + ys + '点。' + t.name + 'の位置">' +
        Object.keys(q.types).map(function(c){ return '<span class="quad-cell quad-' + c + '"' + (q.types[c] === t ? ' data-on' : '') + '>' + q.types[c].name + '</span>'; }).join('') +
        '<i class="quad-vx" style="left:' + mx + '%"></i><i class="quad-hy" style="bottom:' + my + '%"></i><b class="quad-dot" style="left:' + px + '%;bottom:' + py + '%;background:' + t.color + '"></b></div>' +
        '<p class="quad-axis"><span>← ' + kx.name + ' 低い</span><span>高い →</span></p>';
      if (t.tori) tori.unshift(t.tori);
      resultEl.querySelector('.tori-list').innerHTML = tori.map(function(x){ return '<li>' + x + '</li>'; }).join('');
      if (toriBox) toriBox.style.display = '';
    }
    var shareText = encodeURIComponent(data.shareTitle + ' → ' + summary);
    var url = encodeURIComponent(location.href);
    resultEl.querySelector('.share-twitter').href = 'https://twitter.com/intent/tweet?text=' + shareText + '&url=' + url;
    resultEl.querySelector('.share-line').href = 'https://social-plugins.line.me/lineit/share?url=' + url + '&text=' + shareText;

    var saved = false;
    try {
      var p = loadProfile();
      p[slug] = {key: top.k, name: summary, color: color, at: today(), scores: scores};
      localStorage.setItem(PROFILE_KEY, JSON.stringify(p));
      saved = true;
    } catch (e) {}
    var note = resultEl.querySelector('.profile-note');
    note.innerHTML = saved
      ? '<b>診断プロフィール帳に記録しました</b><span>' + Object.keys(loadProfile()).length + '本の診断を記録済み・プロフィール帳を見る →</span>'
      : '<b>診断プロフィール帳</b><span>全部の結果を1枚にまとめる →</span>';
  }

  // summary はJSONに関数を書けないので、尺度ごとの方式で決める
  data.summary = function(top, keys){
    if (data.summaryMode === 'single') {
      var k = Object.keys(keys)[0];
      return keys[k].name + '：' + top.lv.label;
    }
    return 'いちばん高かったのは' + keys[top.k].name;
  };

  if (introEl && slug) {
    var prev = loadProfile()[slug];
    if (prev && startBtn) {
      var prevEl = document.createElement('p');
      prevEl.className = 'prev-result';
      prevEl.innerHTML = '前回の結果: <b style="color:' + prev.color + '">' + prev.name + '</b>（' + prev.at + '）';
      startBtn.parentNode.insertBefore(prevEl, startBtn.nextSibling);
    }
  }

  if (data.pick && norms) {
    var chips = document.querySelectorAll('.pick-chip');
    var setPick = function(btn){
      chips.forEach(function(c){ c.setAttribute('aria-pressed', c === btn); });
      normSel[data.pick.axis] = btn.dataset.id;
      pickLabel = btn.textContent;
      renderQuestion();
    };
    chips.forEach(function(btn){
      btn.addEventListener('click', function(){ setPick(btn); });
      if (btn.dataset.id === normSel[data.pick.axis]) setPick(btn);
    });
    if (!pickLabel && chips.length) setPick(chips[0]);
  }

  startBtn.addEventListener('click', function(){
    introEl.style.display = 'none';
    progressWrap.style.display = 'block';
    listEl.style.display = 'block';
    window.scrollTo({top: 0, behavior: 'smooth'});
  });

  resultEl.querySelector('.retry-btn').addEventListener('click', function(){
    answers = new Array(total).fill(null);
    current = 0;
    progressWrap.style.display = 'block';
    listEl.style.display = 'block';
    resultEl.style.display = 'none';
    renderQuestion();
    window.scrollTo({top: 0, behavior: 'smooth'});
  });

  renderQuestion();
})();
