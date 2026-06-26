import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

const _anthropicApiKey = String.fromEnvironment('ANTHROPIC_API_KEY');

// グローバルシングルトン — アプリ起動時に初期化して再利用
final _tts = FlutterTts();
final _stt = SpeechToText();

const _bg = Color(0xFF0A1628);
const _card = Color(0xFF0F2040);
const _accent = Color(0xFF2196F3);
const _accent2 = Color(0xFF64B5F6);
const _text = Color(0xFFE3F2FD);

const _hiraganaRows = [
  ['あ', 'い', 'う', 'え', 'お'],
  ['か', 'き', 'く', 'け', 'こ'],
  ['さ', 'し', 'す', 'せ', 'そ'],
  ['た', 'ち', 'つ', 'て', 'と'],
  ['な', 'に', 'ぬ', 'ね', 'の'],
  ['は', 'ひ', 'ふ', 'へ', 'ほ'],
  ['ま', 'み', 'む', 'め', 'も'],
  ['や', '', 'ゆ', '', 'よ'],
  ['ら', 'り', 'る', 'れ', 'ろ'],
  ['わ', '', '', '', 'を'],
  ['ん', '', '', '', ''],
];

const _hiraganaWords = {
  'あ': ('あめ', 'ame', 'rain'),
  'い': ('いぬ', 'inu', 'dog'),
  'う': ('うみ', 'umi', 'sea'),
  'え': ('えき', 'eki', 'station'),
  'お': ('おに', 'oni', 'demon'),
  'か': ('かさ', 'kasa', 'umbrella'),
  'き': ('きつね', 'kitsune', 'fox'),
  'く': ('くも', 'kumo', 'cloud'),
  'け': ('けいたい', 'keitai', 'phone'),
  'こ': ('こども', 'kodomo', 'child'),
  'さ': ('さかな', 'sakana', 'fish'),
  'し': ('しんかんせん', 'shinkansen', 'bullet train'),
  'す': ('すし', 'sushi', 'sushi'),
  'せ': ('せんせい', 'sensei', 'teacher'),
  'そ': ('そら', 'sora', 'sky'),
  'た': ('たこ', 'tako', 'octopus'),
  'ち': ('ちず', 'chizu', 'map'),
  'つ': ('つき', 'tsuki', 'moon'),
  'て': ('てがみ', 'tegami', 'letter'),
  'と': ('とり', 'tori', 'bird'),
  'な': ('なまえ', 'namae', 'name'),
  'に': ('にわ', 'niwa', 'garden'),
  'ぬ': ('ぬいぐるみ', 'nuigurumi', 'stuffed animal'),
  'ね': ('ねこ', 'neko', 'cat'),
  'の': ('のり', 'nori', 'seaweed'),
  'は': ('はな', 'hana', 'flower'),
  'ひ': ('ひと', 'hito', 'person'),
  'ふ': ('ふじさん', 'fujisan', 'Mt. Fuji'),
  'へ': ('へや', 'heya', 'room'),
  'ほ': ('ほし', 'hoshi', 'star'),
  'ま': ('まど', 'mado', 'window'),
  'み': ('みず', 'mizu', 'water'),
  'む': ('むし', 'mushi', 'insect'),
  'め': ('めがね', 'megane', 'glasses'),
  'も': ('もり', 'mori', 'forest'),
  'や': ('やま', 'yama', 'mountain'),
  'ゆ': ('ゆき', 'yuki', 'snow'),
  'よ': ('よる', 'yoru', 'night'),
  'ら': ('らーめん', 'ramen', 'ramen'),
  'り': ('りんご', 'ringo', 'apple'),
  'る': ('るーぷ', 'loop', 'loop'),
  'れ': ('れいぞうこ', 'reizouko', 'refrigerator'),
  'ろ': ('ろうそく', 'rousoku', 'candle'),
  'わ': ('わに', 'wani', 'crocodile'),
  'を': ('をんな', 'onna', 'woman'),
  'ん': ('ん', 'n', '(nasal sound)'),
};

const _quizData = [
  ('apple', 'りんご', 'ringo', '🍎'),
  ('cat', 'ねこ', 'neko', '🐱'),
  ('dog', 'いぬ', 'inu', '🐶'),
  ('rain', 'あめ', 'ame', '🌧'),
  ('moon', 'つき', 'tsuki', '🌙'),
  ('fish', 'さかな', 'sakana', '🐟'),
  ('snow', 'ゆき', 'yuki', '❄️'),
  ('star', 'ほし', 'hoshi', '⭐'),
  ('bird', 'とり', 'tori', '🐦'),
  ('flower', 'はな', 'hana', '🌸'),
  ('water', 'みず', 'mizu', '💧'),
  ('mountain', 'やま', 'yama', '⛰'),
  ('sea', 'うみ', 'umi', '🌊'),
  ('night', 'よる', 'yoru', '🌙'),
  ('forest', 'もり', 'mori', '🌲'),
];

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // TTS・STT をアプリ起動時に並列初期化
  await Future.wait([
    _tts.setLanguage('ja-JP'),
    _stt.initialize(),
  ]);
  runApp(const HiraganaApp());
}

class HiraganaApp extends StatelessWidget {
  const HiraganaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hiragana AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: _bg,
        colorScheme: const ColorScheme.dark(primary: _accent, secondary: _accent2),
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 24),
            const Text(
              'Hiragana AI',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: _accent),
            ),
            const SizedBox(height: 8),
            const Text(
              'Choose a mode to start learning',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14, color: Colors.white54),
            ),
            const SizedBox(height: 24),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  _ModeCard(
                    icon: Icons.auto_stories,
                    label: 'Learn',
                    desc: 'Tap hiragana\nto learn words',
                    color: _accent,
                    onTap: () => Navigator.push(context,
                        MaterialPageRoute(builder: (_) => const LearnPage())),
                  ),
                  const SizedBox(width: 12),
                  _ModeCard(
                    icon: Icons.mic,
                    label: 'Speak',
                    desc: 'Listen & repeat\nwith AI feedback',
                    color: _accent2,
                    onTap: () => Navigator.push(context,
                        MaterialPageRoute(builder: (_) => const SpeakPage())),
                  ),
                  const SizedBox(width: 12),
                  _ModeCard(
                    icon: Icons.image,
                    label: 'Quiz',
                    desc: 'See an image\ntype the word',
                    color: const Color(0xFF1565C0),
                    onTap: () => Navigator.push(context,
                        MaterialPageRoute(builder: (_) => const QuizPage())),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text('Hiragana Chart',
                    style: TextStyle(
                        fontSize: 16, fontWeight: FontWeight.bold, color: _text)),
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: _hiraganaRows.length,
                itemBuilder: (_, i) {
                  final row = _hiraganaRows[i];
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: row.map((h) {
                        if (h.isEmpty) return const SizedBox(width: 56, height: 56);
                        return RepaintBoundary(child: _HiraganaCell(character: h));
                      }).toList(),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ModeCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String desc;
  final Color color;
  final VoidCallback onTap;

  const _ModeCard({
    required this.icon,
    required this.label,
    required this.desc,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: _card,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: color.withValues(alpha: 0.4)),
          ),
          child: Column(
            children: [
              Icon(icon, color: color, size: 28),
              const SizedBox(height: 8),
              Text(label,
                  style: TextStyle(
                      color: color, fontWeight: FontWeight.bold, fontSize: 14)),
              const SizedBox(height: 4),
              Text(desc,
                  style: const TextStyle(color: Colors.white54, fontSize: 11),
                  textAlign: TextAlign.center),
            ],
          ),
        ),
      ),
    );
  }
}

class _HiraganaCell extends StatelessWidget {
  final String character;
  const _HiraganaCell({required this.character});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => LearnDetailPage(character: character)),
      ),
      child: Container(
        width: 56,
        height: 56,
        decoration: BoxDecoration(
          color: _card,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: _accent.withValues(alpha: 0.3)),
        ),
        child: Center(
          child: Text(character,
              style: const TextStyle(fontSize: 24, color: _text)),
        ),
      ),
    );
  }
}

// ── Learn Page ───────────────────────────────────────────────────────────────

class LearnPage extends StatelessWidget {
  const LearnPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Learn Hiragana'), backgroundColor: _bg),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _hiraganaRows.length,
        itemBuilder: (_, i) {
          final row = _hiraganaRows[i];
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: row.map((h) {
                if (h.isEmpty) return const SizedBox(width: 64, height: 64);
                return RepaintBoundary(
                  child: GestureDetector(
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (_) => LearnDetailPage(character: h)),
                    ),
                    child: Container(
                      width: 64,
                      height: 64,
                      decoration: BoxDecoration(
                        color: _card,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: _accent.withValues(alpha: 0.4)),
                      ),
                      child: Center(
                        child: Text(h,
                            style: const TextStyle(fontSize: 28, color: _text)),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          );
        },
      ),
    );
  }
}

class LearnDetailPage extends StatefulWidget {
  final String character;
  const LearnDetailPage({super.key, required this.character});

  @override
  State<LearnDetailPage> createState() => _LearnDetailPageState();
}

class _LearnDetailPageState extends State<LearnDetailPage> {
  @override
  void initState() {
    super.initState();
    _playWord();
  }

  Future<void> _playWord() async {
    final word = _hiraganaWords[widget.character];
    if (word == null) return;
    await _tts.speak(word.$1);
  }

  @override
  void dispose() {
    _tts.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final word = _hiraganaWords[widget.character];
    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(backgroundColor: _bg, elevation: 0),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 160,
              height: 160,
              decoration: BoxDecoration(
                color: _card,
                borderRadius: BorderRadius.circular(32),
                border: Border.all(color: _accent, width: 2),
              ),
              child: Center(
                child: Text(widget.character,
                    style: const TextStyle(fontSize: 100, color: _text)),
              ),
            ),
            const SizedBox(height: 32),
            if (word != null) ...[
              Text(word.$1,
                  style: const TextStyle(
                      fontSize: 40, color: _text, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text(word.$2,
                  style: const TextStyle(fontSize: 22, color: Colors.white54)),
              const SizedBox(height: 4),
              Text(word.$3,
                  style: const TextStyle(fontSize: 18, color: _accent2)),
              const SizedBox(height: 40),
              ElevatedButton.icon(
                onPressed: _playWord,
                icon: const Icon(Icons.volume_up),
                label: const Text('Play again'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _accent,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 32, vertical: 14),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

// ── Speak Page ───────────────────────────────────────────────────────────────

class SpeakPage extends StatefulWidget {
  const SpeakPage({super.key});

  @override
  State<SpeakPage> createState() => _SpeakPageState();
}

class _SpeakPageState extends State<SpeakPage> {
  late String _currentChar;
  late (String, String, String) _currentWord;
  bool _listening = false;
  String _heard = '';
  String? _feedback;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _pickRandom();
  }

  void _pickRandom() {
    final entries = _hiraganaWords.entries
        .where((e) => e.key != 'ん' && e.key != 'を')
        .toList()
      ..shuffle();
    _currentChar = entries.first.key;
    _currentWord = entries.first.value;
    _heard = '';
    _feedback = null;
  }

  Future<void> _playWord() async {
    await _tts.speak(_currentWord.$1);
  }

  Future<void> _startListening() async {
    setState(() {
      _listening = true;
      _heard = '';
      _feedback = null;
    });
    _stt.listen(
      listenOptions: SpeechListenOptions(localeId: 'ja-JP'),
      onResult: (result) {
        setState(() => _heard = result.recognizedWords);
        if (result.finalResult) _stopListening();
      },
    );
  }

  Future<void> _stopListening() async {
    await _stt.stop();
    setState(() => _listening = false);
    if (_heard.isNotEmpty) _checkWithAI();
  }

  Future<void> _checkWithAI() async {
    setState(() => _loading = true);
    try {
      final res = await http.post(
        Uri.parse('https://api.anthropic.com/v1/messages'),
        headers: {
          'x-api-key': _anthropicApiKey,
          'anthropic-version': '2023-06-01',
          'content-type': 'application/json',
        },
        body: jsonEncode({
          'model': 'claude-haiku-4-5-20251001',
          'max_tokens': 80,
          'messages': [
            {
              'role': 'user',
              'content':
                  'The target Japanese word is "${_currentWord.$1}" (${_currentWord.$2}). '
                  'The learner said: "$_heard". '
                  'Reply ONLY with: "Correct!" or "Try again! The word is ${_currentWord.$2}."',
            }
          ],
        }),
      );
      final data = jsonDecode(res.body);
      setState(() => _feedback = data['content'][0]['text']);
    } catch (_) {
      final normalized = _heard.replaceAll(' ', '');
      setState(() => _feedback = normalized == _currentWord.$1
          ? 'Correct!'
          : 'Try again! The word is ${_currentWord.$2}.');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  void dispose() {
    _tts.stop();
    _stt.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isCorrect = _feedback?.startsWith('Correct') ?? false;
    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(title: const Text('Speak & Repeat'), backgroundColor: _bg),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 140,
                height: 140,
                decoration: BoxDecoration(
                  color: _card,
                  borderRadius: BorderRadius.circular(28),
                  border: Border.all(color: _accent2, width: 2),
                ),
                child: Center(
                  child: Text(_currentChar,
                      style: const TextStyle(fontSize: 88, color: _text)),
                ),
              ),
              const SizedBox(height: 24),
              Text(_currentWord.$1,
                  style: const TextStyle(
                      fontSize: 36, color: _text, fontWeight: FontWeight.bold)),
              Text(_currentWord.$2,
                  style: const TextStyle(fontSize: 20, color: Colors.white54)),
              const SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: _playWord,
                icon: const Icon(Icons.volume_up),
                label: const Text('Listen'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _accent,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10)),
                ),
              ),
              const SizedBox(height: 32),
              GestureDetector(
                onTap: _listening ? _stopListening : _startListening,
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: _listening ? _accent2 : _card,
                    shape: BoxShape.circle,
                    border: Border.all(color: _accent2, width: 2),
                  ),
                  child: Icon(_listening ? Icons.stop : Icons.mic,
                      color: Colors.white, size: 36),
                ),
              ),
              const SizedBox(height: 8),
              Text(_listening ? 'Listening...' : 'Tap to speak',
                  style: const TextStyle(color: Colors.white54, fontSize: 13)),
              if (_heard.isNotEmpty) ...[
                const SizedBox(height: 16),
                Text('You said: $_heard',
                    style: const TextStyle(color: Colors.white70, fontSize: 14)),
              ],
              const SizedBox(height: 16),
              if (_loading)
                const CircularProgressIndicator(color: _accent)
              else if (_feedback != null)
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                  decoration: BoxDecoration(
                    color: isCorrect
                        ? Colors.green.withValues(alpha: 0.2)
                        : Colors.red.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                    border:
                        Border.all(color: isCorrect ? Colors.green : Colors.red),
                  ),
                  child: Text(_feedback!,
                      style: TextStyle(
                          color: isCorrect
                              ? Colors.greenAccent
                              : Colors.redAccent,
                          fontSize: 16)),
                ),
              const SizedBox(height: 24),
              TextButton(
                onPressed: () => setState(_pickRandom),
                child: const Text('Next word',
                    style: TextStyle(color: _accent)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Quiz Page ────────────────────────────────────────────────────────────────

class QuizPage extends StatefulWidget {
  const QuizPage({super.key});

  @override
  State<QuizPage> createState() => _QuizPageState();
}

class _QuizPageState extends State<QuizPage> {
  late (String, String, String, String) _current;
  final TextEditingController _ctrl = TextEditingController();
  String? _result;
  int _score = 0;
  int _total = 0;

  @override
  void initState() {
    super.initState();
    _pickRandom();
  }

  void _pickRandom() {
    final list = [..._quizData]..shuffle();
    _current = list.first;
    _ctrl.clear();
    _result = null;
  }

  void _check() {
    final answer = _ctrl.text.trim();
    final correct = answer == _current.$2 || answer == _current.$3;
    setState(() {
      _total++;
      if (correct) _score++;
      _result = correct
          ? 'Correct! ${_current.$2} (${_current.$3})'
          : 'Wrong! The answer is ${_current.$2} (${_current.$3})';
    });
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isCorrect = _result?.startsWith('Correct') ?? false;
    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        title: const Text('Image Quiz'),
        backgroundColor: _bg,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Center(
              child: Text('$_score / $_total',
                  style: const TextStyle(
                      color: _accent,
                      fontSize: 16,
                      fontWeight: FontWeight.bold)),
            ),
          ),
        ],
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 200,
                height: 200,
                decoration: BoxDecoration(
                  color: _card,
                  borderRadius: BorderRadius.circular(28),
                  border:
                      Border.all(color: const Color(0xFF1565C0), width: 2),
                ),
                child: Center(
                  child:
                      Text(_current.$4, style: const TextStyle(fontSize: 100)),
                ),
              ),
              const SizedBox(height: 16),
              const Text('What is this in hiragana?',
                  style: TextStyle(color: Colors.white54, fontSize: 14)),
              const SizedBox(height: 8),
              Text(_current.$1,
                  style: const TextStyle(
                      color: _text,
                      fontSize: 24,
                      fontWeight: FontWeight.bold)),
              const SizedBox(height: 24),
              TextField(
                controller: _ctrl,
                style: const TextStyle(color: _text, fontSize: 24),
                textAlign: TextAlign.center,
                decoration: InputDecoration(
                  hintText: 'Type in hiragana or romaji',
                  hintStyle: const TextStyle(color: Colors.white30),
                  filled: true,
                  fillColor: _card,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: _accent),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: _accent, width: 2),
                  ),
                ),
                onSubmitted: (_) =>
                    _result == null ? _check() : setState(_pickRandom),
              ),
              const SizedBox(height: 16),
              if (_result == null)
                ElevatedButton(
                  onPressed: _check,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1565C0),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 40, vertical: 14),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('Check', style: TextStyle(fontSize: 16)),
                )
              else ...[
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 20, vertical: 12),
                  decoration: BoxDecoration(
                    color: isCorrect
                        ? Colors.green.withValues(alpha: 0.2)
                        : Colors.red.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                        color: isCorrect ? Colors.green : Colors.red),
                  ),
                  child: Text(
                    _result!,
                    style: TextStyle(
                        color: isCorrect
                            ? Colors.greenAccent
                            : Colors.redAccent,
                        fontSize: 15),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => setState(_pickRandom),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _accent,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 40, vertical: 14),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('Next', style: TextStyle(fontSize: 16)),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
