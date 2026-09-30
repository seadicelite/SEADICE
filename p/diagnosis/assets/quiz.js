(function(){
  var dataEl = document.getElementById('quiz-data');
  if (!dataEl) return;
  var data = JSON.parse(dataEl.textContent);
  var listEl = document.getElementById('quiz-questions');
  var resultEl = document.getElementById('quiz-result');
  var progressBar = document.getElementById('quiz-progress-bar');
  var progressLabel = document.getElementById('quiz-progress-label');
  var progressWrap = document.getElementById('quiz-progress-wrap');
  var introEl = document.getElementById('quiz-intro');
  var startBtn = document.getElementById('quiz-start-btn');

  var total = data.questions.length;
  var typeKeys = Object.keys(data.types);
  var answers = new Array(total).fill(null);
  var current = 0;

  var ICONS = [
    '<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="8" fill="#fff" fill-opacity=".9"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none"><rect x="5" y="5" width="14" height="14" rx="4" transform="rotate(45 12 12)" fill="#fff" fill-opacity=".9"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none"><polygon points="12,4 20,20 4,20" fill="#fff" fill-opacity=".9"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none"><polygon points="12,3 20,8 20,16 12,21 4,16 4,8" fill="#fff" fill-opacity=".9"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none"><path d="M12 2l2.4 7.2H22l-6 4.6 2.3 7.2L12 16.4 5.7 21l2.3-7.2-6-4.6h7.6z" fill="#fff" fill-opacity=".9"/></svg>',
    '<svg viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="6" fill="#fff" fill-opacity=".9"/></svg>'
  ];

  function updateProgress(){
    var pct = (current / total) * 100;
    progressBar.style.width = pct + '%';
    progressLabel.textContent = Math.min(current + 1, total) + ' / ' + total;
  }

  function renderQuestion(){
    updateProgress();
    listEl.innerHTML = '';
    var q = data.questions[current];
    var block = document.createElement('div');
    block.className = 'q-block';
    var title = document.createElement('p');
    title.className = 'q-title';
    title.innerHTML = '<span class="q-num">Q' + (current + 1) + '</span>' + q.q;
    block.appendChild(title);

    var optList = document.createElement('div');
    optList.className = 'q-opt-list';
    q.options.forEach(function(opt, oi){
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'q-opt';
      btn.innerHTML = '<span class="q-opt-dot"></span><span>' + opt.text + '</span>';
      btn.addEventListener('click', function(){
        answers[current] = oi;
        if (current < total - 1) {
          current++;
          renderQuestion();
        } else {
          showResult();
        }
      });
      optList.appendChild(btn);
    });
    block.appendChild(optList);

    var back = document.createElement('button');
    back.type = 'button';
    back.className = 'q-back';
    back.textContent = '← 前の質問に戻る';
    back.disabled = current === 0;
    back.addEventListener('click', function(){
      if (current > 0) { current--; renderQuestion(); }
    });
    block.appendChild(back);

    listEl.appendChild(block);
  }

  function showResult(){
    var scores = {};
    typeKeys.forEach(function(k){ scores[k] = 0; });
    data.questions.forEach(function(q, qi){
      var oi = answers[qi];
      if (oi === null) return;
      var opt = q.options[oi];
      scores[opt.type] = (scores[opt.type] || 0) + (opt.weight || 1);
    });
    var bestKey = typeKeys[0];
    typeKeys.forEach(function(k){ if (scores[k] > scores[bestKey]) bestKey = k; });
    var t = data.types[bestKey];
    var typeIndex = typeKeys.indexOf(bestKey);

    progressWrap.style.display = 'none';
    listEl.style.display = 'none';
    resultEl.style.display = 'block';
    var card = resultEl.querySelector('.result-card');
    card.style.setProperty('--type-color', t.color || '#ff6b81');
    resultEl.querySelector('.result-icon').innerHTML = ICONS[typeIndex % ICONS.length];
    resultEl.querySelector('.result-type').textContent = data.resultLabel || '診断結果';
    resultEl.querySelector('.result-name').textContent = t.name;
    resultEl.querySelector('.result-desc').innerHTML = t.desc;
    var shareText = encodeURIComponent(data.shareTitle + ' → 結果は「' + t.name + '」でした');
    var url = encodeURIComponent(location.href);
    resultEl.querySelector('.share-twitter').href = 'https://twitter.com/intent/tweet?text=' + shareText + '&url=' + url;
    resultEl.querySelector('.share-line').href = 'https://social-plugins.line.me/lineit/share?url=' + url + '&text=' + shareText;
    window.scrollTo({top: 0, behavior: 'smooth'});
  }

  if (startBtn) {
    startBtn.addEventListener('click', function(){
      introEl.style.display = 'none';
      progressWrap.style.display = 'block';
      listEl.style.display = 'block';
      window.scrollTo({top: 0, behavior: 'smooth'});
    });
  }

  var retryBtn = resultEl.querySelector('.retry-btn');
  if (retryBtn) {
    retryBtn.addEventListener('click', function(){
      answers = new Array(total).fill(null);
      current = 0;
      progressWrap.style.display = 'block';
      listEl.style.display = 'block';
      resultEl.style.display = 'none';
      renderQuestion();
      window.scrollTo({top: 0, behavior: 'smooth'});
    });
  }

  renderQuestion();
})();
