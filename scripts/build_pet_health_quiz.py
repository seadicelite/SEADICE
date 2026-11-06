#!/usr/bin/env python3
"""ペット健康クイズの問題を、サイトとアプリに書き出す。

元データ: scripts/pet_health_quiz.json（出典は照合済みのものだけ）
書き出し先:
  - p/tools/pet-health/index.html の「quiz data」と「refs」の間
  - ~/Developer/ペット系/pet_kenko_quiz/lib/quiz_bank.dart（アプリがあるときだけ）
"""
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'scripts' / 'pet_health_quiz.json'
PAGE = ROOT / 'p' / 'tools' / 'pet-health' / 'index.html'
APP = Path.home() / 'Developer' / 'ペット系' / 'pet_kenko_quiz' / 'lib' / 'quiz_bank.dart'


def js(v):
    return json.dumps(v, ensure_ascii=False, separators=(',', ':'))


def dart(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'").replace('$', '\\$') + "'"


def build_page(d):
    s = PAGE.read_text(encoding='utf-8')
    src = {k: [v[0], v[2]] for k, v in d['sources'].items()}
    qs = [[q['pet'], q['ja']['q'], q['ja']['a'], q['ja']['w'], q['ja']['e'], q['src']] for q in d['questions']]
    block = ('// BEGIN quiz data（scripts/build_pet_health_quiz.py が書き出す。手で直さない）\n'
             '// Q: [対象 d=犬 c=猫 b=両方, 問題, 正解, 誤答3つ, 解説, 出典]\n'
             'var S=' + js(src) + ';\nvar Q=[\n' + ',\n'.join(js(q) for q in qs) + '\n];\n// END quiz data\n')
    s, n = re.subn(r'// BEGIN quiz data.*?// END quiz data\n', lambda m: block, s, flags=re.S)
    assert n == 1, 'quiz data の印が見つからない'
    used = []
    for q in d['questions']:
        for k in q['src']:
            if k not in used:
                used.append(k)
    refs = ''.join(f'<li><a href="{d["sources"][k][2]}" rel="noopener">{d["sources"][k][0]}</a></li>' for k in used)
    s, n = re.subn(r'(<!-- refs:begin -->).*?(<!-- refs:end -->)', lambda m: m.group(1) + refs + m.group(2), s, flags=re.S)
    assert n == 1, 'refs の印が見つからない'
    PAGE.write_text(s, encoding='utf-8')
    pets = [q['pet'] for q in d['questions']]
    print(f'page: {len(qs)}問（犬 {pets.count("d") + pets.count("b")}・猫 {pets.count("c") + pets.count("b")}）')


def build_app(d):
    if not APP.parent.exists():
        print('app: フォルダがないので飛ばした')
        return
    out = ['// 自動生成: SEADICE/scripts/build_pet_health_quiz.py（元データ scripts/pet_health_quiz.json）。手で直さない。',
           '',
           'class BankText {',
           '  final String question;',
           '  final List<String> choices;',
           '  final int answer;',
           '  final String explanation;',
           '  const BankText(this.question, this.choices, this.answer, this.explanation);',
           '}',
           '',
           'class BankQuestion {',
           '  final String id;',
           "  final String pet; // d=犬 c=猫 b=両方",
           '  final BankText ja;',
           '  final BankText en;',
           '  final List<String> sources;',
           '  const BankQuestion(this.id, this.pet, this.ja, this.en, this.sources);',
           '}',
           '',
           '/// 出典: キー → (日本語名, 英語名, URL)',
           'const bankSources = <String, (String, String, String)>{']
    for k, v in d['sources'].items():
        out.append(f'  {dart(k)}: ({dart(v[0])}, {dart(v[1])}, {dart(v[2])}),')
    out += ['};', '', f"const bankChecked = {dart(d['checked'])};", '', 'const bankQuestions = <BankQuestion>[']
    for q in d['questions']:
        order = list(range(4))
        random.Random(q['id']).shuffle(order)
        texts = []
        for lang in ('ja', 'en'):
            t = q[lang]
            opts = [t['a']] + t['w']
            choices = [opts[i] for i in order]
            texts.append(f"BankText({dart(t['q'])}, [{', '.join(dart(c) for c in choices)}], {order.index(0)}, {dart(t['e'])})")
        out.append(f"  BankQuestion({dart(q['id'])}, {dart(q['pet'])},\n      {texts[0]},\n      {texts[1]},\n      [{', '.join(dart(k) for k in q['src'])}]),")
    out.append('];')
    APP.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'app: {APP}')


if __name__ == '__main__':
    data = json.loads(DATA.read_text(encoding='utf-8'))
    for q in data['questions']:
        for k in q['src']:
            assert k in data['sources'], (q['id'], k)
        for lang in ('ja', 'en'):
            assert len(q[lang]['w']) == 3, (q['id'], lang)
    build_page(data)
    build_app(data)
