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
    lead.textContent = data.lead;
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

  function showResult(){
    var keys = Object.keys(data.keys);
    var scores = {};
    keys.forEach(function(k){ scores[k] = 0; });
    data.items.forEach(function(it, i){
      var v = answers[i];
      scores[it.key] += it.reverse ? (points + 1 - v) : v;
    });

    var html = '';
    var tori = [];
    var top = null;
    keys.forEach(function(k){
      var d = data.keys[k], s = scores[k], lv = levelOf(s, d), t = lv.band || d[lv.id];
      if (!top || lv.z > top.z) top = {k: k, z: lv.z, lv: lv};
      var pos = (s - d.min) / (d.max - d.min) * 100;
      var mean = d.mean != null ? (d.mean - d.min) / (d.max - d.min) * 100 : null;
      html += '<div class="sc-item sc-' + lv.id + '">' +
        '<p class="sc-head"><span class="sc-name">' + d.name + '</span><span class="sc-level">' + lv.label + '（' + s + '点）</span></p>' +
        '<div class="sc-bar" role="img" aria-label="' + d.name + ' ' + s + '点（' + d.min + '〜' + d.max + '点' + (mean != null ? '、平均' + d.mean + '点' : '') + '）"><i style="width:' + pos + '%"></i>' + (mean != null ? '<b style="left:' + mean + '%"></b>' : '') + '</div>' +
        '<p class="sc-desc">' + t.desc + '</p></div>';
      tori.push(t.tori);
    });

    progressWrap.style.display = 'none';
    listEl.style.display = 'none';
    resultEl.style.display = 'block';
    resultEl.querySelector('.sc-list').innerHTML = html;
    resultEl.querySelector('.tori-list').innerHTML = tori.map(function(t){ return '<li>' + t + '</li>'; }).join('');

    var summary = data.summary(top, data.keys);
    var shareText = encodeURIComponent(data.shareTitle + ' → ' + summary);
    var url = encodeURIComponent(location.href);
    resultEl.querySelector('.share-twitter').href = 'https://twitter.com/intent/tweet?text=' + shareText + '&url=' + url;
    resultEl.querySelector('.share-line').href = 'https://social-plugins.line.me/lineit/share?url=' + url + '&text=' + shareText;

    var saved = false;
    try {
      var p = loadProfile();
      p[slug] = {key: top.k, name: summary, color: data.keys[top.k].color, at: new Date().toISOString().slice(0, 10), scores: scores};
      localStorage.setItem(PROFILE_KEY, JSON.stringify(p));
      saved = true;
    } catch (e) {}
    var note = resultEl.querySelector('.profile-note');
    note.innerHTML = saved
      ? '<b>診断プロフィール帳に記録しました</b><span>' + Object.keys(loadProfile()).length + '本の診断を記録済み・プロフィール帳を見る →</span>'
      : '<b>診断プロフィール帳</b><span>全部の結果を1枚にまとめる →</span>';
    window.scrollTo({top: 0, behavior: 'smooth'});
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
