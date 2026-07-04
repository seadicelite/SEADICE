import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:http/http.dart' as http;

// NotoSansJP フォールバックを全 GoogleFonts スタイルに付与する Extension
extension _JaFallback on TextStyle {
  TextStyle get ja => copyWith(fontFamilyFallback: const ['NotoSansJP']);
}

// ──────────────────────────────────────────────
// モデル
// ──────────────────────────────────────────────
class AppItem {
  final int id;
  final String title;
  final String tag;
  final String desc;
  final Color color;
  final String icon;
  final double? rating;
  final String? downloads;
  final String? appStore;
  final String? playStore;
  final String? webUrl;
  final String status;
  final String? imageAsset;

  AppItem({
    required this.id,
    required this.title,
    required this.tag,
    required this.desc,
    required this.color,
    required this.icon,
    this.rating,
    this.downloads,
    this.appStore,
    this.playStore,
    this.webUrl,
    required this.status,
    this.imageAsset,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'title': title,
        'tag': tag,
        'desc': desc,
        'colorValue': color.toARGB32(),
        'icon': icon,
        'rating': rating,
        'downloads': downloads,
        'appStore': appStore,
        'playStore': playStore,
        'webUrl': webUrl,
        'status': status,
        'imageAsset': imageAsset,
      };

  factory AppItem.fromJson(Map<String, dynamic> j) => AppItem(
        id: j['id'],
        title: j['title'],
        tag: j['tag'],
        desc: j['desc'],
        color: Color(j['colorValue']),
        icon: j['icon'],
        rating: j['rating']?.toDouble(),
        downloads: j['downloads'],
        appStore: j['appStore'],
        playStore: j['playStore'],
        webUrl: j['webUrl'],
        status: j['status'],
        imageAsset: j['imageAsset'],
      );
}

// ──────────────────────────────────────────────
// 定数
// ──────────────────────────────────────────────
const _bg      = Color(0xFF05050C);
const _accent  = Color(0xFF00FFD1);
const _accent2 = Color(0xFF38BDF8);

// ブレークポイント
const _kMd = 600.0;   // スマホ大〜タブレット
const _kLg = 900.0;   // デスクトップ

// レスポンシブヘルパー
double _hPad(double w) => w < _kMd ? w * 0.05 : w < _kLg ? 48.0 : w * 0.1;

double _vPad(double w) => w < _kMd ? 60.0 : 100.0;

final _defaultApps = [
  // ── Apps (status: WEB / LIVE) ─────────────────────────────────────
  AppItem(
    id: 24,
    title: '超ズボラ日記',
    tag: 'Lifestyle',
    desc: '一言書くだけ。AIが日記に整えてGoogleカレンダーへ自動保存。広告を見て投稿するズボラ向けiOSアプリ。',
    color: const Color(0xFFFF6B9D),
    icon: '日記',
    webUrl: 'https://seadice.win/apps/chozubora/',
    status: 'LIVE',
  ),
  AppItem(
    id: 19,
    title: 'ドローンCBT対策',
    tag: 'Education',
    desc: 'ドローン・無人航空機の国家試験CBT対策アプリ。分散学習（SM-2）で航空法・技能証明の重要事項を効率的に暗記できる。',
    color: const Color(0xFF3B82F6),
    icon: 'UAV',
    webUrl: 'https://seadice.win/drone/anki/',
    status: 'WEB',
    imageAsset: 'assets/apps/drone_cbt.png',
  ),
  AppItem(
    id: 13,
    title: '楽々暗記',
    tag: 'Education',
    desc: 'スペーシング復習（SRS）搭載のフラッシュカード暗記アプリ。SM-2アルゴリズムで効率的に記憶を定着させる。',
    color: const Color(0xFF00FFD1),
    icon: 'SRS',
    webUrl: 'https://seadice.win/rakuraku/',
    status: 'WEB',
    imageAsset: 'assets/apps/rakuraku.png',
  ),
  AppItem(
    id: 12,
    title: 'TOITE',
    tag: 'Education',
    desc: '問題をスナップして即座にAI解答。写真を撮るだけでClaudeが解き方をステップ解説。毎日5回まで無料、広告視聴で回数追加。',
    color: const Color(0xFF4F6EF7),
    icon: 'AI',
    status: 'LIVE',
    imageAsset: 'assets/apps/toite.png',
  ),
  AppItem(
    id: 15,
    title: '貿易実務検定C級',
    tag: 'Education',
    desc: '貿易実務検定C級の模擬試験・大問別演習が無料でできるWebアプリ。本番形式で繰り返し練習して合格を目指せる。',
    color: const Color(0xFF10A37F),
    icon: '貿',
    webUrl: 'https://seadice.win/boueki-hub/',
    status: 'WEB',
    imageAsset: 'assets/apps/boueki.png',
  ),
  AppItem(
    id: 16,
    title: '顔タイプ診断',
    tag: 'AI',
    desc: '顔のパーツ・骨格・髪型からAIが性格や印象を分析。写真1枚で、あなたの顔が持つ本質的な特徴を読み解きます。',
    color: const Color(0xFFEC4899),
    icon: '顔',
    webUrl: 'https://seadice.win/kao_type_diag/',
    status: 'WEB',
    imageAsset: 'assets/apps/face_type.png',
  ),
  AppItem(
    id: 17,
    title: 'ピラミッドタスク管理',
    tag: 'Productivity',
    desc: '目標をピラミッド構造に分解して「今やるべきこと」を見える化。夢を最下層のTODOまで落とし込み、一歩ずつ前進できる目標管理アプリ。',
    color: const Color(0xFF00FFD1),
    icon: 'TASK',
    webUrl: 'https://seadice.win/jinsei_pyramid/',
    status: 'WEB',
    imageAsset: 'assets/apps/pyramid.png',
  ),
  AppItem(
    id: 20,
    title: 'TikDog',
    tag: 'Entertainment',
    desc: '犬動画をTikTokスタイルで無限にスワイプ。かわいい・おもしろい犬動画だけを集めたバーティカル動画アプリ。',
    color: const Color(0xFFFF6B35),
    icon: 'DOG',
    appStore: 'https://apps.apple.com/jp/app/tikdog/id6748308505',
    webUrl: 'https://seadice.win/tikdog/',
    status: 'LIVE',
    imageAsset: 'assets/apps/tikdog.png',
  ),
  // ── Native Apps (status: LIVE) ───────────────────────────────────
  AppItem(
    id: 18,
    title: "Life's RPG",
    tag: 'Productivity',
    desc: '人生をRPGに変える習慣管理アプリ。タスク・フォーカス・ルールの達成でダンジョンの敵にダメージを与え、レベルアップしながら目標を攻略。',
    color: const Color(0xFFD4A017),
    icon: 'RPG',
    webUrl: 'https://seadice.win/lifeisrpg/',
    status: 'WEB',
    imageAsset: 'assets/apps/life_is_rpg.png',
  ),
  // ── Mini Apps (status: MINI) ──────────────────────────────────────
  AppItem(
    id: 14,
    title: '言い訳ジェネレーター',
    tag: 'AI',
    desc: 'シチュエーションを選ぶだけで、AIが笑えるけどリアルな言い訳を即生成。遅刻・締め切り遅れ・欠席…どんな場面もカバー。',
    color: const Color(0xFFA78BFA),
    icon: 'AI',
    status: 'MINI',
    imageAsset: 'assets/apps/excuse_generator.png',
  ),
];



// アプリID → 遊べるミニアプリWidget
final _miniApps = <int, Widget Function()>{
  14: () => const ExcuseGeneratorMini(),
};

// ──────────────────────────────────────────────
// ストレージ
// ──────────────────────────────────────────────
class AppStorage {
  static const _key = 'seadice_apps';

  static Future<List<AppItem>> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key);
    if (raw == null) return List.from(_defaultApps);
    try {
      final list = jsonDecode(raw) as List;
      final apps = list.map((e) => AppItem.fromJson(e)).toList();
      // _defaultApps に追加されたアプリを保存済みデータにマージ
      final savedIds = apps.map((a) => a.id).toSet();
      for (final app in _defaultApps) {
        if (!savedIds.contains(app.id)) apps.add(app);
      }
      // デフォルトの status / webUrl / imageAsset 変更をマイグレーション
      final defaultMap = {for (final a in _defaultApps) a.id: a};
      for (int i = 0; i < apps.length; i++) {
        final def = defaultMap[apps[i].id];
        if (def != null) {
          final needsMigration = apps[i].status != def.status ||
              apps[i].webUrl != def.webUrl ||
              apps[i].imageAsset != def.imageAsset;
          if (needsMigration) {
            apps[i] = AppItem(
              id: apps[i].id, title: apps[i].title, tag: apps[i].tag,
              desc: apps[i].desc, color: apps[i].color, icon: apps[i].icon,
              rating: apps[i].rating, downloads: apps[i].downloads,
              appStore: apps[i].appStore, playStore: apps[i].playStore,
              webUrl: def.webUrl,
              imageAsset: def.imageAsset,
              status: def.status,
            );
          }
        }
      }
      return apps;
    } catch (_) {
      return List.from(_defaultApps);
    }
  }

  static Future<void> save(List<AppItem> apps) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, jsonEncode(apps.map((a) => a.toJson()).toList()));
  }
}

// ──────────────────────────────────────────────
// Global gear rotation（全インスタンス共有）
// ──────────────────────────────────────────────
final _gearTurns = ValueNotifier<double>(0.0);

void _startGearRotation() {
  Timer.periodic(const Duration(milliseconds: 40), (_) {
    _gearTurns.value = (_gearTurns.value + 40 / 8000) % 1.0;
  });
}

// ──────────────────────────────────────────────
// Router
// ──────────────────────────────────────────────
final _router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomePage(),
    ),
    GoRoute(
      path: '/apps/:id',
      builder: (context, state) {
        final app = state.extra as AppItem?;
        if (app == null) return const HomePage();
        return AppDetailPage(app: app);
      },
    ),
    GoRoute(
      path: '/privacy',
      builder: (context, state) => const PrivacyPage(),
    ),
    GoRoute(
      path: '/privacy/toite',
      builder: (context, state) => const ToitePrivacyPage(),
    ),
    GoRoute(
      path: '/privacy/:appId',
      builder: (context, state) =>
          AppPrivacyPage(appId: state.pathParameters['appId']!),
    ),
    GoRoute(
      path: '/order',
      builder: (context, state) => const OrderPage(),
    ),
  ],
);

// ──────────────────────────────────────────────
// main
// ──────────────────────────────────────────────
void main() {
  _startGearRotation();
  runApp(const SeaDiceApp());
}

class SeaDiceApp extends StatelessWidget {
  const SeaDiceApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'SEADICE',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        scaffoldBackgroundColor: _bg,
        colorScheme: const ColorScheme.dark(primary: _accent),
        textTheme: GoogleFonts.dmSansTextTheme(ThemeData.dark().textTheme)
            .apply(fontFamilyFallback: ['NotoSansJP']),
      ),
      routerConfig: _router,
    );
  }
}


// ──────────────────────────────────────────────
// RevealOnScroll
// ──────────────────────────────────────────────
class RevealOnScroll extends StatefulWidget {
  final Widget child;
  final ScrollController scrollCtrl;
  final double triggerOffset;

  const RevealOnScroll({
    super.key,
    required this.child,
    required this.scrollCtrl,
    this.triggerOffset = 0.88,
  });

  @override
  State<RevealOnScroll> createState() => _RevealOnScrollState();
}

class _RevealOnScrollState extends State<RevealOnScroll>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _opacity;
  late Animation<double> _slide;
  bool _triggered = false;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 550));
    _opacity = CurvedAnimation(parent: _ctrl, curve: Curves.easeOut);
    _slide = Tween(begin: 32.0, end: 0.0)
        .animate(CurvedAnimation(parent: _ctrl, curve: Curves.easeOutCubic));
    widget.scrollCtrl.addListener(_check);
    WidgetsBinding.instance.addPostFrameCallback((_) => _check());
  }

  @override
  void dispose() {
    widget.scrollCtrl.removeListener(_check);
    _ctrl.dispose();
    super.dispose();
  }

  void _check() {
    if (_triggered || !mounted) return;
    final box = context.findRenderObject() as RenderBox?;
    if (box == null || !box.attached) return;
    final pos = box.localToGlobal(Offset.zero);
    if (pos.dy < MediaQuery.of(context).size.height * widget.triggerOffset) {
      _triggered = true;
      _ctrl.forward();
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (_, child) => Opacity(
        opacity: _opacity.value,
        child: Transform.translate(
          offset: Offset(0, _slide.value),
          child: child,
        ),
      ),
      child: widget.child,
    );
  }
}

// ──────────────────────────────────────────────
// Home Page
// ──────────────────────────────────────────────
class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final _scrollCtrl = ScrollController();
  double _scrollProgress = 0.0;
  List<AppItem> _apps = [];
  bool _loading = true;

  final _heroKey    = GlobalKey();
  final _appsKey    = GlobalKey();
  final _aboutKey   = GlobalKey();
  final _contactKey = GlobalKey();

  @override
  void initState() {
    super.initState();
    _load();
    _scrollCtrl.addListener(_onScroll);
  }

  void _onScroll() {
    final max = _scrollCtrl.position.maxScrollExtent;
    if (max <= 0) return;
    setState(() => _scrollProgress = _scrollCtrl.offset / max);
  }

  @override
  void dispose() {
    _scrollCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final apps = await AppStorage.load();
    setState(() { _apps = apps; _loading = false; });
  }

  void _scrollTo(GlobalKey key) {
    final ctx = key.currentContext;
    if (ctx == null) return;
    Scrollable.ensureVisible(
        ctx, duration: const Duration(milliseconds: 700), curve: Curves.easeInOut);
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        backgroundColor: _bg,
        body: const Center(child: _SpinningGear(size: 64)),
      );
    }

    return Scaffold(
      backgroundColor: _bg,
      body: Stack(
        children: [
          SingleChildScrollView(
            controller: _scrollCtrl,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 64),
                HeroSection(key: _heroKey),
                const VisionSection(),
                RevealOnScroll(
                  scrollCtrl: _scrollCtrl,
                  child: AppsSection(
                    key: _appsKey,
                    apps: _apps,
                  ),
                ),
                RevealOnScroll(
                  scrollCtrl: _scrollCtrl,
                  child: AboutSection(key: _aboutKey, apps: _apps),
                ),
                RevealOnScroll(
                  scrollCtrl: _scrollCtrl,
                  child: ContactSection(key: _contactKey),
                ),
                _footer(),
              ],
            ),
          ),
          // スクロール進捗バー
          Positioned(
            top: 0, left: 0, right: 0,
            child: FractionallySizedBox(
              widthFactor: _scrollProgress,
              alignment: Alignment.centerLeft,
              child: Container(
                height: 2,
                decoration: const BoxDecoration(
                  gradient: LinearGradient(colors: [_accent, _accent2]),
                  boxShadow: [BoxShadow(color: Color(0x8000FFD1), blurRadius: 6)],
                ),
              ),
            ),
          ),
          Positioned(
            top: 0, left: 0, right: 0,
            child: Navbar(
              onNav: (section) {
                if (section == 'TOOLS') {
                  launchUrl(Uri.parse('https://seadice.win/tools/'), mode: LaunchMode.externalApplication);
                  return;
                }
                final keys = {
                  'APPS':    _appsKey,
                  'ABOUT':   _aboutKey,
                  'CONTACT': _contactKey,
                };
                _scrollTo(keys[section]!);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _footer() {
    final w = MediaQuery.of(context).size.width;
    return Container(
      padding: EdgeInsets.symmetric(horizontal: w * 0.06, vertical: 20),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Color(0x14FFFFFF))),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text('© 2026 SEADICE',
              style: GoogleFonts.spaceMono(fontSize: 11, color: Colors.white24).ja),
          Text('Built with Flutter × ♥',
              style: GoogleFonts.spaceMono(fontSize: 11, color: Colors.white24).ja),
        ],
      ),
    );
  }

}

// ──────────────────────────────────────────────
// Navbar（レスポンシブ + backdrop blur）
// ──────────────────────────────────────────────
class Navbar extends StatefulWidget {
  final void Function(String) onNav;

  const Navbar({
    super.key,
    required this.onNav,
  });

  @override
  State<Navbar> createState() => _NavbarState();
}

class _NavbarState extends State<Navbar> with SingleTickerProviderStateMixin {
  bool _menuOpen = false;
  late AnimationController _menuCtrl;
  late Animation<double> _menuAnim;

  @override
  void initState() {
    super.initState();
    _menuCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 280));
    _menuAnim =
        CurvedAnimation(parent: _menuCtrl, curve: Curves.easeInOut);
  }

  @override
  void dispose() {
    _menuCtrl.dispose();
    super.dispose();
  }

  void _toggleMenu() {
    setState(() => _menuOpen = !_menuOpen);
    _menuOpen ? _menuCtrl.forward() : _menuCtrl.reverse();
  }

  void _closeMenu() {
    if (!_menuOpen) return;
    setState(() => _menuOpen = false);
    _menuCtrl.reverse();
  }

  @override
  Widget build(BuildContext context) {
    final isMobile = MediaQuery.of(context).size.width < 700;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // ── ヘッダーバー ──
        ClipRect(
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
            child: Container(
              height: 64,
              padding: const EdgeInsets.symmetric(horizontal: 24),
              decoration: BoxDecoration(
                color: _bg.withValues(alpha: 0.72),
                border: const Border(
                    bottom: BorderSide(color: Color(0x1A00FFD1))),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const _SpinningGear(size: 28),
                  const SizedBox(width: 10),
                  Text(
                    'SEADICE',
                    style: GoogleFonts.spaceMono(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: _accent,
                        letterSpacing: 1.2).ja,
                  ),
                  const Spacer(),
                  if (!isMobile) ...[
                    for (final item in ['APPS', 'ABOUT', 'CONTACT', 'TOOLS'])
                      _NavLink(label: item, onTap: () => widget.onNav(item)),
                  ] else ...[
                    GestureDetector(
                      onTap: _toggleMenu,
                      child: SizedBox(
                        width: 36,
                        height: 36,
                        child: AnimatedIcon(
                          icon: AnimatedIcons.menu_close,
                          progress: _menuAnim,
                          color: Colors.white70,
                          size: 22,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
        // ── モバイルメニュー ──
        if (isMobile)
          SizeTransition(
            sizeFactor: _menuAnim,
            child: ClipRect(
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
                child: Container(
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: _bg.withValues(alpha: 0.92),
                    border: const Border(
                        bottom: BorderSide(color: Color(0x1A00FFD1))),
                  ),
                  child: Column(
                    children: [
                      for (final item in ['APPS', 'ABOUT', 'CONTACT', 'TOOLS'])
                        _MobileNavItem(
                          label: item,
                          onTap: () {
                            _closeMenu();
                            widget.onNav(item);
                          },
                        ),
                      const SizedBox(height: 6),
                    ],
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}

class _NavLink extends StatefulWidget {
  final String label;
  final VoidCallback onTap;
  const _NavLink({required this.label, required this.onTap});
  @override
  State<_NavLink> createState() => _NavLinkState();
}

class _NavLinkState extends State<_NavLink> {
  bool _hov = false;
  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hov = true),
      onExit: (_) => setState(() => _hov = false),
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: widget.onTap,
        child: SizedBox(
          height: 64,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14),
            child: Center(
              child: AnimatedDefaultTextStyle(
                duration: const Duration(milliseconds: 200),
                style: GoogleFonts.spaceMono(
                    fontSize: 11,
                    letterSpacing: 2,
                    color: _hov ? _accent : Colors.white54).ja,
                child: Text(widget.label),
              ),
            ),
          ),
        ),
      ),
    );
  }
}


class _MobileNavItem extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  const _MobileNavItem({required this.label, required this.onTap});
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 18),
        decoration: BoxDecoration(
          border: Border(
              top: BorderSide(color: Colors.white.withValues(alpha: 0.06))),
        ),
        child: Text(
          label,
          style: GoogleFonts.spaceMono(
              fontSize: 13, letterSpacing: 3, color: Colors.white70).ja,
        ),
      ),
    );
  }
}

// ──────────────────────────────────────────────
// DiceIcon
// ──────────────────────────────────────────────
class DiceIcon extends StatefulWidget {
  final double size;
  final bool animated;
  final Color color;
  const DiceIcon(
      {super.key, this.size = 40, this.animated = false, this.color = _accent});
  @override
  State<DiceIcon> createState() => _DiceIconState();
}

class _DiceIconState extends State<DiceIcon>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _rot;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 600));
    _rot = Tween<double>(begin: 0, end: 0).animate(
        CurvedAnimation(parent: _ctrl, curve: Curves.elasticOut));
    if (widget.animated) _startLoop();
  }

  final _angles = [0.0, 0.35, -0.26, 0.17];
  int _idx = 0;

  void _startLoop() {
    Future.delayed(const Duration(milliseconds: 2200), () {
      if (!mounted) return;
      _idx = (_idx + 1) % _angles.length;
      _rot = Tween<double>(begin: _rot.value, end: _angles[_idx])
          .animate(CurvedAnimation(parent: _ctrl, curve: Curves.elasticOut));
      _ctrl.forward(from: 0);
      _startLoop();
    });
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _rot,
      builder: (_, _) => Transform.rotate(
        angle: _rot.value,
        child: CustomPaint(
          size: Size(widget.size, widget.size),
          painter: _DicePainter(color: widget.color),
        ),
      ),
    );
  }
}

class _DicePainter extends CustomPainter {
  final Color color;
  _DicePainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final s = size.width;
    final stroke = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = s * 0.06;
    canvas.drawRRect(
      RRect.fromRectAndRadius(
          Rect.fromLTWH(s * 0.075, s * 0.075, s * 0.85, s * 0.85),
          Radius.circular(s * 0.2)),
      stroke,
    );
    final dot = Paint()..color = color..style = PaintingStyle.fill;
    final r = s * 0.063;
    for (final pos in [
      Offset(s * 0.3, s * 0.3), Offset(s * 0.7, s * 0.3),
      Offset(s * 0.5, s * 0.5),
      Offset(s * 0.3, s * 0.7), Offset(s * 0.7, s * 0.7),
    ]) {
      canvas.drawCircle(pos, r, dot);
    }
  }

  @override
  bool shouldRepaint(_DicePainter old) => old.color != color;
}

// ──────────────────────────────────────────────
// Spinning Gear Logo（グローバルタイマー共有）
// ──────────────────────────────────────────────
class _SpinningGear extends StatelessWidget {
  final double size;
  const _SpinningGear({required this.size});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<double>(
      valueListenable: _gearTurns,
      builder: (_, turns, child) => Transform.rotate(
        angle: turns * 2 * pi,
        child: child,
      ),
      child: Icon(Icons.settings, size: size, color: _accent),
    );
  }
}

// ──────────────────────────────────────────────
// Vision Section
// ──────────────────────────────────────────────
const _visionSlides = [
  (
    title: 'Robotics',
    sub: 'ロボットに関連するホットな記事まとめてます。ロボットの最前線を知りたい方はどうぞ。',
    url: 'https://robo.seadice.win',
    colors: [Color(0xFF040A06), Color(0xFF081410)],
    accent: Color(0xFF00FF88),
  ),
];

class VisionSection extends StatefulWidget {
  const VisionSection({super.key});
  @override
  State<VisionSection> createState() => _VisionSectionState();
}

class _VisionSectionState extends State<VisionSection> {
  int _current = 0;
  Timer? _timer;
  late final PageController _pageCtrl;

  @override
  void initState() {
    super.initState();
    _pageCtrl = PageController();
    _timer = Timer.periodic(const Duration(seconds: 4), (_) => _next());
  }

  @override
  void dispose() {
    _timer?.cancel();
    _pageCtrl.dispose();
    super.dispose();
  }

  void _next() {
    if (!mounted) return;
    final next = (_current + 1) % _visionSlides.length;
    _pageCtrl.animateToPage(
      next,
      duration: const Duration(milliseconds: 600),
      curve: Curves.easeInOut,
    );
  }

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    final height = w > 600 ? 420.0 : 280.0;

    return SizedBox(
      height: height,
      child: Stack(
        children: [
          PageView.builder(
            controller: _pageCtrl,
            onPageChanged: (i) => setState(() => _current = i),
            itemCount: _visionSlides.length,
            itemBuilder: (_, i) {
              final s = _visionSlides[i];
              return _VisionSlide(slide: s, screenWidth: w);
            },
          ),
          // ドットインジケーター（2枚以上のときのみ表示）
          if (_visionSlides.length > 1)
          Positioned(
            bottom: 24, left: 0, right: 0,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(_visionSlides.length, (i) {
                final active = i == _current;
                return GestureDetector(
                  onTap: () => _pageCtrl.animateToPage(
                    i,
                    duration: const Duration(milliseconds: 400),
                    curve: Curves.easeInOut,
                  ),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 250),
                    margin: const EdgeInsets.symmetric(horizontal: 4),
                    width: active ? 24 : 6,
                    height: 6,
                    decoration: BoxDecoration(
                      color: active
                          ? _visionSlides[_current].accent
                          : Colors.white.withValues(alpha: 0.3),
                      borderRadius: BorderRadius.circular(3),
                    ),
                  ),
                );
              }),
            ),
          ),
        ],
      ),
    );
  }
}

class _VisionSlide extends StatelessWidget {
  final ({
    String title,
    String sub,
    String url,
    List<Color> colors,
    Color accent
  }) slide;
  final double screenWidth;
  const _VisionSlide({required this.slide, required this.screenWidth});

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: () => launchUrl(Uri.parse(slide.url), mode: LaunchMode.externalApplication),
        child: Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: slide.colors,
        ),
      ),
      child: Stack(
        children: [
          // 回路基板グリッド
          Positioned.fill(child: CustomPaint(painter: _CircuitPainter(slide.accent))),
          // グロウ（左下）
          Positioned(
            bottom: -80, left: -80,
            child: _GlowOrb(color: slide.accent, size: 340),
          ),
          // ロボットアイコン（右背景）
          Positioned(
            right: screenWidth > 600 ? screenWidth * 0.06 : 12,
            top: 0, bottom: 0,
            child: Center(
              child: Icon(
                Icons.precision_manufacturing_outlined,
                size: screenWidth > 600 ? 200 : 110,
                color: slide.accent.withValues(alpha: 0.07),
              ),
            ),
          ),
          // コンテンツ
          Padding(
            padding: EdgeInsets.symmetric(
              horizontal: screenWidth > 600 ? screenWidth * 0.08 : 24,
              vertical: 48,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Row(children: [
                  Container(width: 24, height: 1, color: slide.accent),
                  const SizedBox(width: 10),
                  Text('WORKS',
                      style: GoogleFonts.spaceMono(
                          fontSize: 10, letterSpacing: 3, color: slide.accent).ja),
                ]),
                const SizedBox(height: 16),
                Text(slide.title,
                    style: GoogleFonts.syne(
                        fontSize: screenWidth > 600 ? 42 : 28,
                        fontWeight: FontWeight.w800,
                        color: Colors.white,
                        height: 1.1,
                        letterSpacing: -1).ja),
                const SizedBox(height: 12),
                Text(slide.sub,
                    style: GoogleFonts.dmSans(
                        fontSize: 14,
                        color: Colors.white.withValues(alpha: 0.55),
                        height: 1.6).ja),
                const SizedBox(height: 24),
                Row(children: [
                  Text('VISIT SITE',
                      style: GoogleFonts.spaceMono(
                          fontSize: 10, letterSpacing: 3,
                          color: slide.accent.withValues(alpha: 0.75)).ja),
                  const SizedBox(width: 8),
                  Icon(Icons.arrow_forward, size: 12,
                      color: slide.accent.withValues(alpha: 0.75)),
                ]),
              ],
            ),
          ),
        ],
      ),
        ),
      ),
    );
  }
}

// ──────────────────────────────────────────────
// Hero Section
// ──────────────────────────────────────────────
class HeroSection extends StatefulWidget {
  const HeroSection({super.key});
  @override
  State<HeroSection> createState() => _HeroSectionState();
}

class _HeroSectionState extends State<HeroSection>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _fade;
  late Animation<double> _slide;

  int _typedTotal = 0;
  Timer? _typingTimer;
  static const _titleLines = ['CRAFT', 'APPS', 'THAT', 'ROLL.'];
  static const _totalChars = 18;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 600));
    _fade = CurvedAnimation(parent: _ctrl, curve: Curves.easeOut);
    _slide = Tween(begin: 24.0, end: 0.0)
        .animate(CurvedAnimation(parent: _ctrl, curve: Curves.easeOutCubic));
    _ctrl.forward().then((_) {
      if (mounted) _startTyping();
    });
  }

  void _startTyping() {
    _typingTimer = Timer.periodic(const Duration(milliseconds: 55), (timer) {
      if (!mounted) { timer.cancel(); return; }
      if (_typedTotal >= _totalChars) { timer.cancel(); return; }
      setState(() => _typedTotal++);
    });
  }

  @override
  void dispose() {
    _typingTimer?.cancel();
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (_, child) => Opacity(
        opacity: _fade.value,
        child: Transform.translate(
          offset: Offset(0, _slide.value),
          child: child,
        ),
      ),
      child: Container(
        constraints: BoxConstraints(minHeight: w > 600 ? 600 : 400),
        padding: EdgeInsets.symmetric(horizontal: w * 0.06, vertical: w > 600 ? 80 : 52),
        child: Stack(
          children: [
            Positioned.fill(child: CustomPaint(painter: _GridPainter())),
            Positioned(
                top: 0, right: 0, child: _GlowOrb(color: _accent, size: 420)),
            Positioned(
                bottom: 0,
                left: 0,
                child: _GlowOrb(color: const Color(0xFFA78BFA), size: 300)),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(children: [
                  Container(width: 24, height: 1, color: _accent),
                  const SizedBox(width: 10),
                  Flexible(
                    child: Text(
                      'APP DEVELOPMENT / INDIVIDUAL',
                      style: GoogleFonts.spaceMono(
                          fontSize: 11, letterSpacing: w > 400 ? 4 : 1.5, color: _accent).ja,
                    ),
                  ),
                ]),
                const SizedBox(height: 20),
                _buildTitle(w),
                const SizedBox(height: 36),
                _OrderBanner(),
              ],
            ),
            Positioned(
              right: 20, bottom: 20,
              child: Opacity(
                opacity: 0.12,
                child: _SpinningGear(size: w > 600 ? 160 : 80),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTitle(double w) {
    final fs = w > 900 ? 80.0 : w > 600 ? 64.0 : w > 400 ? 48.0 : 38.0;
    const configs = [
      (false, false),
      (true,  false),
      (false, false),
      (false, true),
    ];

    int charsBefore = 0;
    final rows = <Widget>[];

    for (int i = 0; i < _titleLines.length; i++) {
      final text     = _titleLines[i];
      final outline  = configs[i].$1;
      final gradient = configs[i].$2;
      final shown    = (_typedTotal - charsBefore).clamp(0, text.length);
      final display  = text.substring(0, shown);
      final isLast   = i == _titleLines.length - 1;
      final isCursor = _typedTotal >= charsBefore &&
          (_typedTotal < charsBefore + text.length ||
              (_typedTotal >= _totalChars && isLast));
      charsBefore += text.length;

      Widget textWidget;
      if (gradient) {
        textWidget = ShaderMask(
          shaderCallback: (b) => const LinearGradient(
            colors: [_accent, _accent2],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ).createShader(b),
          child: Text(display,
              style: GoogleFonts.syne(
                  fontSize: fs, fontWeight: FontWeight.w800,
                  height: 1.0, color: Colors.white, letterSpacing: -1).ja),
        );
      } else if (outline) {
        textWidget = Text(display,
            style: GoogleFonts.syne(
                fontSize: fs, fontWeight: FontWeight.w800,
                height: 1.0, letterSpacing: -1,
                foreground: Paint()
                  ..style = PaintingStyle.stroke
                  ..strokeWidth = 2
                  ..color = _accent.withValues(alpha: 0.8)).ja);
      } else {
        textWidget = Text(display,
            style: GoogleFonts.syne(
                fontSize: fs, fontWeight: FontWeight.w800,
                height: 1.0, color: Colors.white, letterSpacing: -1).ja);
      }

      rows.add(SizedBox(
        height: fs,
        child: Row(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            textWidget,
            if (isCursor) _BlinkingCursor(height: fs * 0.82),
          ],
        ),
      ));
    }

    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: rows);
  }
}

class _BlinkingCursor extends StatefulWidget {
  final double height;
  const _BlinkingCursor({required this.height});
  @override
  State<_BlinkingCursor> createState() => _BlinkingCursorState();
}

class _BlinkingCursorState extends State<_BlinkingCursor> {
  bool _visible = true;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(const Duration(milliseconds: 530), (_) {
      if (mounted) setState(() => _visible = !_visible);
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedOpacity(
      opacity: _visible ? 1.0 : 0.0,
      duration: const Duration(milliseconds: 80),
      child: Container(
        width: 3,
        height: widget.height,
        margin: const EdgeInsets.only(left: 6),
        decoration: BoxDecoration(
          color: _accent,
          borderRadius: BorderRadius.circular(2),
        ),
      ),
    );
  }
}

class _GridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = _accent.withValues(alpha: 0.04)
      ..strokeWidth = 1;
    const step = 60.0;
    for (double x = 0; x < size.width; x += step) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (double y = 0; y < size.height; y += step) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(_) => false;
}

class _CircuitPainter extends CustomPainter {
  final Color color;
  const _CircuitPainter(this.color);

  @override
  void paint(Canvas canvas, Size size) {
    final grid = Paint()
      ..color = color.withValues(alpha: 0.04)
      ..strokeWidth = 0.5;
    const step = 36.0;
    for (double x = 0; x < size.width; x += step) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), grid);
    }
    for (double y = 0; y < size.height; y += step) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), grid);
    }

    final nodeFill = Paint()..color = color.withValues(alpha: 0.30);
    final nodeRing = Paint()
      ..color = color.withValues(alpha: 0.14)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    final trace = Paint()
      ..color = color.withValues(alpha: 0.13)
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;

    const nodes = [
      (108.0, 72.0), (216.0, 36.0), (324.0, 108.0),
      (72.0, 180.0), (180.0, 144.0), (288.0, 216.0),
      (360.0, 72.0), (144.0, 252.0), (252.0, 288.0),
    ];
    for (final n in nodes) {
      final o = Offset(n.$1, n.$2);
      canvas.drawCircle(o, 2.5, nodeFill);
      canvas.drawCircle(o, 6.0, nodeRing);
    }

    final path = Path()
      ..moveTo(108, 72)..lineTo(216, 72)..lineTo(216, 36)
      ..moveTo(72, 180)..lineTo(180, 180)..lineTo(180, 144)
      ..moveTo(288, 216)..lineTo(324, 216)..lineTo(324, 108)
      ..moveTo(144, 252)..lineTo(252, 252)..lineTo(252, 288)
      ..moveTo(360, 72)..lineTo(360, 108);
    canvas.drawPath(path, trace);
  }

  @override
  bool shouldRepaint(_) => false;
}

// ──────────────────────────────────────────────
// Order Banner
// ──────────────────────────────────────────────
class _OrderBanner extends StatefulWidget {
  const _OrderBanner();
  @override
  State<_OrderBanner> createState() => _OrderBannerState();
}

class _OrderBannerState extends State<_OrderBanner> {
  bool _hov = false;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    return MouseRegion(
      onEnter: (_) => setState(() => _hov = true),
      onExit: (_) => setState(() => _hov = false),
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: () => context.go('/order'),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          decoration: BoxDecoration(
            color: _hov
                ? _accent.withValues(alpha: 0.08)
                : Colors.white.withValues(alpha: 0.03),
            border: Border.all(
              color: _hov
                  ? _accent.withValues(alpha: 0.5)
                  : Colors.white.withValues(alpha: 0.1),
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(
                  color: _accent,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 10),
              Text('受注受付中',
                  style: GoogleFonts.spaceMono(
                      fontSize: 11,
                      letterSpacing: 2,
                      color: _accent).ja),
              if (w >= _kMd) ...[
                const SizedBox(width: 16),
                Text('個人向けWebアプリ、買い切り月額¥0',
                    style: GoogleFonts.dmSans(
                        fontSize: 13,
                        color: Colors.white60).ja),
              ],
              const SizedBox(width: 12),
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                transform: Matrix4.translationValues(_hov ? 4 : 0, 0, 0),
                child: const Icon(Icons.arrow_forward,
                    size: 14, color: _accent),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _GlowOrb extends StatelessWidget {
  final Color color;
  final double size;
  const _GlowOrb({required this.color, required this.size});
  @override
  Widget build(BuildContext context) {
    return Container(
      width: size, height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: RadialGradient(
            colors: [color.withValues(alpha: 0.07), Colors.transparent]),
      ),
    );
  }
}

// ──────────────────────────────────────────────
// Apps Section
// ──────────────────────────────────────────────
class AppsSection extends StatefulWidget {
  final List<AppItem> apps;
  const AppsSection({
    super.key,
    required this.apps,
  });
  @override
  State<AppsSection> createState() => _AppsSectionState();
}

class _AppsSectionState extends State<AppsSection> {
  String _tab = 'APP';
  late final PageController _pageCtrl;
  int _carouselPage = 0;

  @override
  void initState() {
    super.initState();
    _pageCtrl = PageController(viewportFraction: 0.85);
  }

  @override
  void dispose() {
    _pageCtrl.dispose();
    super.dispose();
  }

  void _setTab(String tab) {
    setState(() {
      _tab = tab;
      _carouselPage = 0;
    });
    if (_pageCtrl.hasClients) _pageCtrl.jumpToPage(0);
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _tab == 'APP'
        ? widget.apps.where((a) => a.status != 'MINI').toList()
        : widget.apps.where((a) => a.status == 'MINI').toList();
    final w = MediaQuery.of(context).size.width;
    final crossCount = w > 1100 ? 4 : w > 750 ? 3 : w > 500 ? 2 : 1;
    final isMobileLayout = w < 640;

    return Padding(
      padding: EdgeInsets.symmetric(horizontal: w * 0.06, vertical: 80),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _SectionLabel(label: 'APPS'),
          const SizedBox(height: 12),
          Text('App Catalog',
              style: GoogleFonts.syne(
                  fontSize: isMobileLayout ? 36 : 40,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                  letterSpacing: -1).ja),
          const SizedBox(height: 20),
          // APP / MINI タブ
          Row(
            children: [
              _TabButton(
                label: 'Apps',
                active: _tab == 'APP',
                onTap: () => _setTab('APP'),
              ),
              const SizedBox(width: 8),
              _TabButton(
                label: 'Mini Apps',
                active: _tab == 'MINI',
                onTap: () => _setTab('MINI'),
              ),
              const Spacer(),
            ],
          ),
          const SizedBox(height: 24),
          if (filtered.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 48),
              child: Center(
                child: Text('Coming soon...',
                    style: GoogleFonts.spaceMono(
                        fontSize: 13, color: Colors.white24).ja),
              ),
            )
          else if (isMobileLayout) ...[
            SizedBox(
              height: (w * 0.78).clamp(240.0, 320.0),
              child: PageView.builder(
                controller: _pageCtrl,
                onPageChanged: (p) => setState(() => _carouselPage = p),
                itemCount: filtered.length,
                itemBuilder: (_, i) => Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 6),
                  child: AppCard(app: filtered[i], index: i),
                ),
              ),
            ),
            const SizedBox(height: 12),
            // インジケーターdots
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(filtered.length, (i) {
                final active = _carouselPage == i;
                return AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  margin: const EdgeInsets.symmetric(horizontal: 3),
                  width: active ? 16 : 6,
                  height: 6,
                  decoration: BoxDecoration(
                    color: active ? _accent : Colors.white24,
                    borderRadius: BorderRadius.circular(3),
                  ),
                );
              }),
            ),
          ] else
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: crossCount,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 0.72,
              ),
              itemCount: filtered.length,
              itemBuilder: (_, i) => AppCard(
                app: filtered[i],
                index: i,
              ),
            ),
        ],
      ),
    );
  }
}

class _TabButton extends StatelessWidget {
  final String label;
  final bool active;
  final VoidCallback onTap;

  const _TabButton({required this.label, required this.active, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: active ? _accent.withValues(alpha: 0.15) : Colors.transparent,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: active ? _accent.withValues(alpha: 0.5) : Colors.white.withValues(alpha: 0.1),
          ),
        ),
        child: Text(
          label,
          style: GoogleFonts.dmSans(
            fontSize: 13,
            fontWeight: active ? FontWeight.w600 : FontWeight.w400,
            color: active ? _accent : Colors.white54,
          ).ja,
        ),
      ),
    );
  }
}


// ──────────────────────────────────────────────
// App Card
// ──────────────────────────────────────────────
class AppCard extends StatefulWidget {
  final AppItem app;
  final int index;
  const AppCard({
    super.key,
    required this.app,
    required this.index,
  });
  @override
  State<AppCard> createState() => _AppCardState();
}

class _AppCardState extends State<AppCard> {
  double _tiltX = 0, _tiltY = 0;
  bool _hov = false;
  final _cardKey = GlobalKey();

  Color _darken(Color c) {
    final hsl = HSLColor.fromColor(c);
    return hsl.withLightness((hsl.lightness - 0.15).clamp(0, 1)).toColor();
  }

  Matrix4 get _tiltMatrix {
    final m = Matrix4.identity()..setEntry(3, 2, 0.001);
    m.rotateX(_tiltX);
    m.rotateY(_tiltY);
    return m;
  }

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      key: _cardKey,
      onEnter: (_) => setState(() => _hov = true),
      onExit: (_) => setState(() {
        _hov = false;
        _tiltX = 0;
        _tiltY = 0;
      }),
      onHover: (e) {
        final box = _cardKey.currentContext?.findRenderObject() as RenderBox?;
        if (box == null) return;
        final size = box.size;
        final local = box.globalToLocal(e.position);
        setState(() {
          _tiltY = ((local.dx / size.width) - 0.5) * 0.2;
          _tiltX = -((local.dy / size.height) - 0.5) * 0.2;
        });
      },
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: () {
          if (widget.app.webUrl?.isNotEmpty == true) {
            launchUrl(Uri.parse(widget.app.webUrl!),
                mode: LaunchMode.externalApplication);
          } else {
            context.push('/apps/${widget.app.id}', extra: widget.app);
          }
        },
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          transform: _hov
              ? _tiltMatrix
              : Matrix4.translationValues(0, 0, 0),
          decoration: BoxDecoration(
            color: _hov
                ? widget.app.color.withValues(alpha: 0.06)
                : const Color(0x08FFFFFF),
            border: Border.all(
              color: _hov
                  ? widget.app.color
                  : Colors.white.withValues(alpha: 0.07),
              width: 1.5,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _thumbnail(),
              Expanded(child: _content()),
            ],
          ),
        ),
      ),
    );
  }

  Widget _thumbnail() {
    return Container(
      height: 120,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [widget.app.color, _darken(widget.app.color)],
        ),
      ),
      child: Stack(
        children: [
          Container(color: Colors.black.withValues(alpha: 0.15)),
          if (widget.app.imageAsset != null)
            Positioned.fill(
              child: Image.asset(
                widget.app.imageAsset!,
                fit: BoxFit.cover,
                errorBuilder: (_, _, _) => Center(
                  child: Text(widget.app.icon,
                      style: const TextStyle(fontSize: 48,
                          shadows: [Shadow(color: Colors.black45, blurRadius: 12)])),
                ),
              ),
            )
          else
            Center(
              child: Text(widget.app.icon,
                  style: const TextStyle(
                      fontSize: 48,
                      shadows: [Shadow(color: Colors.black45, blurRadius: 12)])),
            ),
          Positioned(
            top: 8, right: 8,
            child: Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: Colors.black.withValues(alpha: 0.55),
                border: Border.all(
                  color: widget.app.status == 'LIVE'
                      ? widget.app.color.withValues(alpha: 0.4)
                      : widget.app.status == 'WEB'
                          ? _accent2.withValues(alpha: 0.7)
                          : const Color(0xFFF59E0B).withValues(alpha: 0.7),
                ),
              ),
              child: Text(
                widget.app.status == 'LIVE'
                    ? '● LIVE'
                    : widget.app.status == 'WEB'
                        ? '◈ WEB'
                        : widget.app.status,
                style: GoogleFonts.spaceMono(
                    fontSize: 9,
                    letterSpacing: 1.2,
                    color: widget.app.status == 'LIVE'
                        ? widget.app.color
                        : widget.app.status == 'WEB'
                            ? _accent2
                            : const Color(0xFFF59E0B)).ja,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _content() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(widget.app.tag,
              style: GoogleFonts.spaceMono(
                  fontSize: 9, letterSpacing: 2.5, color: widget.app.color).ja),
          const SizedBox(height: 4),
          Text(widget.app.title,
              style: GoogleFonts.syne(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                  letterSpacing: -0.3).ja,
              maxLines: 1,
              overflow: TextOverflow.ellipsis),
          const SizedBox(height: 6),
          Expanded(
            child: Text(widget.app.desc,
                style: GoogleFonts.dmSans(
                    fontSize: 12, color: Colors.white38, height: 1.55).ja,
                maxLines: 3,
                overflow: TextOverflow.ellipsis),
          ),
          const SizedBox(height: 8),
          if (widget.app.rating != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _StarRating(rating: widget.app.rating!),
                  if (widget.app.downloads != null)
                    Text('⬇ ${widget.app.downloads}',
                        style: GoogleFonts.spaceMono(
                            fontSize: 9,
                            color: Colors.white24,
                            letterSpacing: 1).ja),
                ],
              ),
            ),
          Wrap(
            spacing: 6, runSpacing: 4,
            children: [
              if (widget.app.appStore?.isNotEmpty == true)
                _StoreChip(
                    label: 'App Store',
                    url: widget.app.appStore!,
                    color: widget.app.color),
              if (widget.app.playStore?.isNotEmpty == true)
                _StoreChip(
                    label: 'Google Play',
                    url: widget.app.playStore!,
                    color: widget.app.color),
              if ((widget.app.appStore?.isEmpty != false) &&
                  (widget.app.playStore?.isEmpty != false))
                Text(
                  widget.app.status == 'WEB' ? '▷ Web で今すぐ試せる' : '近日公開予定',
                  style: GoogleFonts.spaceMono(
                      fontSize: 9,
                      color: widget.app.status == 'WEB'
                          ? _accent2.withValues(alpha: 0.7)
                          : Colors.white24).ja,
                ),
            ],
          ),
        ],
      ),
    );
  }
}


class _StarRating extends StatelessWidget {
  final double rating;
  const _StarRating({required this.rating});
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        ...List.generate(
            5,
            (i) => Icon(
                  i < rating.round() ? Icons.star : Icons.star_border,
                  size: 12,
                  color: i < rating.round()
                      ? const Color(0xFFF59E0B)
                      : Colors.white24,
                )),
        const SizedBox(width: 4),
        Text('$rating',
            style:
                GoogleFonts.spaceMono(fontSize: 9, color: Colors.white38).ja),
      ],
    );
  }
}

class _StoreChip extends StatefulWidget {
  final String label, url;
  final Color color;
  const _StoreChip(
      {required this.label, required this.url, required this.color});
  @override
  State<_StoreChip> createState() => _StoreChipState();
}

class _StoreChipState extends State<_StoreChip> {
  bool _hov = false;
  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hov = true),
      onExit: (_) => setState(() => _hov = false),
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: () => launchUrl(Uri.parse(widget.url)),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
          decoration: BoxDecoration(
            color: widget.color.withValues(alpha: _hov ? 0.22 : 0.1),
            border: Border.all(
                color: widget.color.withValues(alpha: _hov ? 1.0 : 0.35)),
          ),
          child: Text(widget.label,
              style: GoogleFonts.spaceMono(
                  fontSize: 9, letterSpacing: 1, color: widget.color).ja),
        ),
      ),
    );
  }
}

// ──────────────────────────────────────────────
// About Section
// ──────────────────────────────────────────────
class AboutSection extends StatelessWidget {
  final List<AppItem> apps;
  const AboutSection({super.key, required this.apps});

  @override
  Widget build(BuildContext context) {
    final liveCount = apps.length;
    double totalDL = 0;
    for (final a in apps) {
      if (a.downloads == null) continue;
      final n = double.tryParse(a.downloads!.replaceAll('k', '')) ?? 0;
      totalDL += a.downloads!.contains('k') ? n * 1000 : n;
    }
    final fmtDL = totalDL >= 1000
        ? '${(totalDL / 1000).toStringAsFixed(0)}k+'
        : '${totalDL.toInt()}+';
    final ratings = apps
        .where((a) => a.rating != null)
        .map((a) => a.rating!)
        .toList();
    final avgR = ratings.isEmpty
        ? '—'
        : (ratings.reduce((a, b) => a + b) / ratings.length)
            .toStringAsFixed(1);

    final w = MediaQuery.of(context).size.width;
    final stats = [
      ('$liveCount', 'Projects'),
      (fmtDL, 'Total Downloads'),
      ('$avgR★', 'Avg. Rating'),
      ('3yr+', 'Experience'),
    ];

    return Padding(
      padding: EdgeInsets.symmetric(horizontal: w * 0.06, vertical: 80),
      child: w > 800
          ? Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Expanded(child: _aboutText()),
              const SizedBox(width: 60),
              Expanded(child: _statsGrid(stats)),
            ])
          : Column(children: [
              _aboutText(),
              const SizedBox(height: 40),
              _statsGrid(stats)
            ]),
    );
  }

  Widget _aboutText() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SectionLabel(label: 'ABOUT'),
        const SizedBox(height: 8),
        Builder(builder: (context) {
          final w = MediaQuery.of(context).size.width;
          return Text("Hello,\nI'm SEADICE.",
              style: GoogleFonts.syne(
                  fontSize: w > 600 ? 36 : w > 400 ? 28 : 24,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                  height: 1.15,
                  letterSpacing: -0.5).ja);
        }),
        const SizedBox(height: 20),
        Text('「こんなツールがあったら」を、現実へ。',
            style: GoogleFonts.dmSans(
                fontSize: 15, color: Colors.white54, height: 1.8).ja),
        const SizedBox(height: 12),
        Text(
            '「使っていて飽きない」「触るたびに発見がある」——そんなアプリを追求している。あなたの頭の中のアイデアを、世界にひとつだけのWebアプリへ。',
            style: GoogleFonts.dmSans(
                fontSize: 15, color: Colors.white54, height: 1.8).ja),
      ],
    );
  }

  Widget _statsGrid(List<(String, String)> stats) {
    return LayoutBuilder(builder: (context, constraints) {
      final cols = constraints.maxWidth > 500 ? 4 : 2;
      return GridView.count(
      crossAxisCount: cols,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 1.6,
      children: stats
          .map((s) => Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.02),
                  border: Border.all(
                      color: Colors.white.withValues(alpha: 0.07)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    ShaderMask(
                      shaderCallback: (b) => const LinearGradient(
                          colors: [_accent, _accent2]).createShader(b),
                      child: Text(s.$1,
                          style: GoogleFonts.syne(
                              fontSize: 28,
                              fontWeight: FontWeight.w800,
                              color: Colors.white).ja),
                    ),
                    const SizedBox(height: 4),
                    Text(s.$2,
                        style: GoogleFonts.spaceMono(
                            fontSize: 10,
                            color: Colors.white30,
                            letterSpacing: 1.5).ja),
                  ],
                ),
              ))
          .toList(),
      );
    });
  }
}

// ──────────────────────────────────────────────
// Contact Section
// ──────────────────────────────────────────────
class ContactSection extends StatelessWidget {
  const ContactSection({super.key});
  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    final hPad = _hPad(w);
    final titleFs = w > 600 ? 32.0 : w > 400 ? 24.0 : 20.0;
    return Container(
      padding: EdgeInsets.symmetric(horizontal: hPad, vertical: _vPad(w)),
      decoration: const BoxDecoration(
          border: Border(top: BorderSide(color: Color(0x0F00FFD1)))),
      child: Column(
        children: [
          const _SpinningGear(size: 64),
          const SizedBox(height: 24),
          Text("Let's Roll",
              style: GoogleFonts.syne(
                  fontSize: titleFs,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                  letterSpacing: -1).ja),
          ShaderMask(
            shaderCallback: (b) =>
                const LinearGradient(colors: [_accent, _accent2])
                    .createShader(b),
            child: Text('Together.',
                style: GoogleFonts.syne(
                    fontSize: titleFs,
                    fontWeight: FontWeight.w800,
                    color: Colors.white,
                    letterSpacing: -1).ja),
          ),
          const SizedBox(height: 16),
          Text('既存のアプリで満足できないあなたへ、あなた専用のアプリを。',
              style: GoogleFonts.dmSans(
                  fontSize: 15, color: Colors.white38, height: 1.7).ja),
        ],
      ),
    );
  }
}

// ──────────────────────────────────────────────
// Section Label
// ──────────────────────────────────────────────
class _SectionLabel extends StatelessWidget {
  final String label;
  const _SectionLabel({required this.label});
  @override
  Widget build(BuildContext context) {
    return Row(children: [
      Container(width: 24, height: 1, color: _accent),
      const SizedBox(width: 10),
      Text(label,
          style: GoogleFonts.spaceMono(
              fontSize: 11, letterSpacing: 3.5, color: _accent).ja),
    ]);
  }
}

// ──────────────────────────────────────────────
// App Detail Page
// ──────────────────────────────────────────────
class AppDetailPage extends StatelessWidget {
  final AppItem app;
  const AppDetailPage({super.key, required this.app});

  Color _darken(Color c) {
    final hsl = HSLColor.fromColor(c);
    return hsl.withLightness((hsl.lightness - 0.2).clamp(0, 1)).toColor();
  }

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    final hPad = w > 800 ? w * 0.08 : w * 0.05;

    return Scaffold(
      backgroundColor: _bg,
      body: Stack(
        children: [
          // ── コンテンツ ──
          SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ヘッダー画像
                Container(
                  height: w > 600 ? 280 : 200,
                  margin: const EdgeInsets.only(top: 64),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [app.color, _darken(app.color)],
                    ),
                  ),
                  child: Stack(
                    children: [
                      Container(color: Colors.black.withValues(alpha: 0.2)),
                      Positioned.fill(
                          child: CustomPaint(painter: _GridPainter())),
                      if (app.imageAsset != null)
                        Positioned.fill(
                          child: Image.asset(
                            app.imageAsset!,
                            fit: BoxFit.cover,
                            errorBuilder: (_, _, _) => Center(
                              child: Text(app.icon,
                                  style: const TextStyle(fontSize: 80)),
                            ),
                          ),
                        )
                      else
                        Center(
                          child: Text(app.icon,
                              style: const TextStyle(fontSize: 80)),
                        ),
                    ],
                  ),
                ),
                // 詳細コンテンツ
                Padding(
                  padding: EdgeInsets.fromLTRB(hPad, 48, hPad, 80),
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 720),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // タグ
                        Row(children: [
                          Container(width: 20, height: 1, color: app.color),
                          const SizedBox(width: 8),
                          Text(app.tag,
                              style: GoogleFonts.spaceMono(
                                  fontSize: 10,
                                  letterSpacing: 3,
                                  color: app.color).ja),
                        ]),
                        const SizedBox(height: 16),
                        // タイトル
                        Text(app.title,
                            style: GoogleFonts.syne(
                                fontSize: w > 600 ? 40.0 : 28.0,
                                fontWeight: FontWeight.w800,
                                color: Colors.white,
                                letterSpacing: -1).ja),
                        const SizedBox(height: 16),
                        // ステータスバッジ
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: app.status == 'LIVE'
                                ? app.color.withValues(alpha: 0.1)
                                : app.status == 'WEB'
                                    ? _accent2.withValues(alpha: 0.1)
                                    : const Color(0x1AF59E0B),
                            border: Border.all(
                                color: app.status == 'LIVE'
                                    ? app.color
                                    : app.status == 'WEB'
                                        ? _accent2
                                        : const Color(0xFFF59E0B)),
                          ),
                          child: Text(
                            app.status == 'LIVE'
                                ? '● LIVE'
                                : app.status == 'WEB'
                                    ? '◈ WEB'
                                    : app.status,
                            style: GoogleFonts.spaceMono(
                                fontSize: 10,
                                letterSpacing: 1.5,
                                color: app.status == 'LIVE'
                                    ? app.color
                                    : app.status == 'WEB'
                                        ? _accent2
                                        : const Color(0xFFF59E0B)).ja,
                          ),
                        ),
                        const SizedBox(height: 32),
                        // 説明文
                        Text(app.desc,
                            style: GoogleFonts.dmSans(
                                fontSize: 16,
                                color: Colors.white70,
                                height: 1.8).ja),
                        const SizedBox(height: 40),
                        // レーティング・DL数
                        if (app.rating != null) ...[
                          Container(
                            padding: const EdgeInsets.all(20),
                            decoration: BoxDecoration(
                              color: Colors.white.withValues(alpha: 0.02),
                              border: Border.all(
                                  color:
                                      Colors.white.withValues(alpha: 0.07)),
                            ),
                            child: Row(
                              children: [
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    _StarRating(rating: app.rating!),
                                    const SizedBox(height: 4),
                                    Text('Rating',
                                        style: GoogleFonts.spaceMono(
                                            fontSize: 9,
                                            color: Colors.white30,
                                            letterSpacing: 1.5).ja),
                                  ],
                                ),
                                if (app.downloads != null) ...[
                                  Container(
                                      width: 1,
                                      height: 36,
                                      color: Colors.white
                                          .withValues(alpha: 0.1),
                                      margin: const EdgeInsets.symmetric(
                                          horizontal: 24)),
                                  Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(app.downloads!,
                                          style: GoogleFonts.syne(
                                              fontSize: 22,
                                              fontWeight: FontWeight.w800,
                                              color: Colors.white).ja),
                                      const SizedBox(height: 4),
                                      Text('Downloads',
                                          style: GoogleFonts.spaceMono(
                                              fontSize: 9,
                                              color: Colors.white30,
                                              letterSpacing: 1.5).ja),
                                    ],
                                  ),
                                ],
                              ],
                            ),
                          ),
                          const SizedBox(height: 40),
                        ],
                        // ── TRY IT（ミニアプリ）──
                        if (_miniApps.containsKey(app.id)) ...[
                          Row(children: [
                            Container(width: 20, height: 1, color: app.color),
                            const SizedBox(width: 8),
                            Text('TRY IT',
                                style: GoogleFonts.spaceMono(
                                    fontSize: 10, letterSpacing: 3,
                                    color: app.color).ja),
                          ]),
                          const SizedBox(height: 24),
                          Container(
                            width: double.infinity,
                            padding: const EdgeInsets.symmetric(
                                vertical: 48, horizontal: 24),
                            decoration: BoxDecoration(
                              color: app.color.withValues(alpha: 0.04),
                              border: Border.all(
                                  color: app.color.withValues(alpha: 0.15)),
                            ),
                            child: _miniApps[app.id]!(),
                          ),
                          const SizedBox(height: 48),
                        ],
                        // ── Web アプリ ──
                        if (app.webUrl?.isNotEmpty == true) ...[
                          Row(children: [
                            Container(width: 20, height: 1, color: app.color),
                            const SizedBox(width: 8),
                            Text('WEB APP',
                                style: GoogleFonts.spaceMono(
                                    fontSize: 10, letterSpacing: 3,
                                    color: app.color).ja),
                          ]),
                          const SizedBox(height: 16),
                          _DetailStoreButton(
                              label: 'Webで今すぐ試す',
                              icon: Icons.open_in_browser_rounded,
                              url: app.webUrl!,
                              color: app.color),
                          const SizedBox(height: 48),
                        ],
                        // ── ストアボタン ──
                        if (app.appStore?.isNotEmpty == true ||
                            app.playStore?.isNotEmpty == true) ...[
                          Text('ダウンロード',
                              style: GoogleFonts.spaceMono(
                                  fontSize: 10,
                                  letterSpacing: 3,
                                  color: Colors.white38).ja),
                          const SizedBox(height: 16),
                          Wrap(
                            spacing: 12, runSpacing: 12,
                            children: [
                              if (app.appStore?.isNotEmpty == true)
                                _DetailStoreButton(
                                    label: 'App Store',
                                    icon: Icons.apple,
                                    url: app.appStore!,
                                    color: app.color),
                              if (app.playStore?.isNotEmpty == true)
                                _DetailStoreButton(
                                    label: 'Google Play',
                                    icon: Icons.android,
                                    url: app.playStore!,
                                    color: app.color),
                            ],
                          ),
                          const SizedBox(height: 48),
                        ],
                        if (app.id == 12) ...[
                          const SizedBox(height: 8),
                          MouseRegion(
                            cursor: SystemMouseCursors.click,
                            child: GestureDetector(
                              onTap: () => context.push('/privacy/toite'),
                              child: Text('プライバシーポリシー',
                                  style: GoogleFonts.spaceMono(
                                      fontSize: 10,
                                      letterSpacing: 1.5,
                                      color: Colors.white24,
                                      decoration: TextDecoration.underline,
                                      decorationColor: Colors.white24).ja),
                            ),
                          ),
                          const SizedBox(height: 24),
                        ],
                        const SizedBox(height: 12),
                        // 戻るリンク
                        MouseRegion(
                          cursor: SystemMouseCursors.click,
                          child: GestureDetector(
                            onTap: () => context.canPop() ? context.pop() : context.go('/'),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.arrow_back,
                                    color: _accent, size: 16),
                                const SizedBox(width: 8),
                                Text('Back to Apps',
                                    style: GoogleFonts.spaceMono(
                                        fontSize: 11,
                                        letterSpacing: 1.5,
                                        color: _accent).ja),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          // ── 上部ナビバー ──
          Positioned(
            top: 0, left: 0, right: 0,
            child: ClipRect(
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
                child: Container(
                  height: 64,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 24),
                  decoration: BoxDecoration(
                    color: _bg.withValues(alpha: 0.72),
                    border: const Border(
                        bottom: BorderSide(color: Color(0x1A00FFD1))),
                  ),
                  child: Row(
                    children: [
                      MouseRegion(
                        cursor: SystemMouseCursors.click,
                        child: GestureDetector(
                          onTap: () => context.canPop() ? context.pop() : context.go('/'),
                          child: Row(children: [
                            const Icon(Icons.arrow_back_ios,
                                color: Colors.white54, size: 14),
                            const SizedBox(width: 4),
                            Text('BACK',
                                style: GoogleFonts.spaceMono(
                                    fontSize: 11,
                                    letterSpacing: 2,
                                    color: Colors.white54).ja),
                          ]),
                        ),
                      ),
                      const Spacer(),
                      const DiceIcon(size: 22),
                      const SizedBox(width: 8),
                      Text('SEADICE',
                          style: GoogleFonts.spaceMono(
                              fontSize: 15,
                              fontWeight: FontWeight.w700,
                              color: _accent,
                              letterSpacing: 1.2).ja),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _DetailStoreButton extends StatefulWidget {
  final String label, url;
  final IconData icon;
  final Color color;
  const _DetailStoreButton(
      {required this.label,
      required this.url,
      required this.icon,
      required this.color});
  @override
  State<_DetailStoreButton> createState() => _DetailStoreButtonState();
}

class _DetailStoreButtonState extends State<_DetailStoreButton> {
  bool _hov = false;
  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hov = true),
      onExit: (_) => setState(() => _hov = false),
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: () {
          final uri = widget.url.startsWith('/')
              ? Uri.base.resolve(widget.url)
              : Uri.parse(widget.url);
          launchUrl(uri);
        },
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          transform: Matrix4.translationValues(0, _hov ? -3 : 0, 0),
          padding:
              const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          decoration: BoxDecoration(
            color: _hov ? widget.color : Colors.transparent,
            border: Border.all(
                color: _hov
                    ? widget.color
                    : widget.color.withValues(alpha: 0.4)),
            boxShadow: _hov
                ? [
                    BoxShadow(
                        color: widget.color.withValues(alpha: 0.2),
                        blurRadius: 20,
                        offset: const Offset(0, 8))
                  ]
                : [],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(widget.icon,
                  color: _hov ? _bg : widget.color, size: 18),
              const SizedBox(width: 10),
              Text(widget.label,
                  style: GoogleFonts.spaceMono(
                      fontSize: 11,
                      letterSpacing: 1.5,
                      fontWeight: FontWeight.w700,
                      color: _hov ? _bg : widget.color).ja),
            ],
          ),
        ),
      ),
    );
  }
}

// ──────────────────────────────────────────────
// TOITE プライバシーポリシー
// ──────────────────────────────────────────────
class ToitePrivacyPage extends StatelessWidget {
  const ToitePrivacyPage({super.key});

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    final hPad = w > 800 ? w * 0.18 : w * 0.06;

    return Scaffold(
      backgroundColor: _bg,
      body: Stack(
        children: [
          SingleChildScrollView(
            child: Padding(
              padding: EdgeInsets.fromLTRB(hPad, 100, hPad, 80),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 720),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(children: [
                      Container(width: 24, height: 1, color: const Color(0xFF4F6EF7)),
                      const SizedBox(width: 10),
                      Text('TOITE', style: GoogleFonts.spaceMono(fontSize: 11, letterSpacing: 3.5, color: const Color(0xFF4F6EF7)).ja),
                    ]),
                    const SizedBox(height: 12),
                    Text('プライバシーポリシー',
                        style: GoogleFonts.syne(fontSize: 36, fontWeight: FontWeight.w800, color: Colors.white, letterSpacing: -1).ja),
                    const SizedBox(height: 8),
                    Text('最終更新日：2026年5月25日',
                        style: GoogleFonts.spaceMono(fontSize: 11, color: Colors.white30).ja),
                    const SizedBox(height: 48),
                    ..._sections.map((s) => _PrivacySection(title: s.$1, body: s.$2)),
                    const SizedBox(height: 48),
                    MouseRegion(
                      cursor: SystemMouseCursors.click,
                      child: GestureDetector(
                        onTap: () => context.canPop() ? context.pop() : context.go('/'),
                        child: Row(mainAxisSize: MainAxisSize.min, children: [
                          const Icon(Icons.arrow_back, color: _accent, size: 16),
                          const SizedBox(width: 8),
                          Text('Back', style: GoogleFonts.spaceMono(fontSize: 11, letterSpacing: 1.5, color: _accent).ja),
                        ]),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            top: 0, left: 0, right: 0,
            child: ClipRect(
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
                child: Container(
                  height: 64,
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  decoration: BoxDecoration(
                    color: _bg.withValues(alpha: 0.72),
                    border: const Border(bottom: BorderSide(color: Color(0x1A00FFD1))),
                  ),
                  child: Row(children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(6),
                      child: const _SpinningGear(size: 28),
                    ),
                    const SizedBox(width: 10),
                    Text('SEADICE', style: GoogleFonts.spaceMono(fontSize: 16, fontWeight: FontWeight.w700, color: _accent, letterSpacing: 1.2).ja),
                  ]),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

const _sections = [
  ('はじめに',
   'このプライバシーポリシーは、SEADICE（以下「当方」）が提供するiOSアプリ「TOITE」（以下「本アプリ」）における個人情報の取り扱いについて説明します。'),
  ('収集する情報',
   '本アプリは、ユーザーが撮影またはアップロードした問題の画像をAI解析のために使用します。氏名・メールアドレス・電話番号などの個人を特定できる情報は収集しません。'),
  ('情報の利用目的',
   '取得した画像は、Anthropic社のClaude Vision APIに送信され、問題の解答・解説を生成するためにのみ使用されます。解答・解説テキストはGoogle Firebaseに保存され、ユーザー自身が履歴として参照できます。'),
  ('広告について',
   '本アプリはGoogle AdMob（Google LLC）による広告を表示します。AdMobは広告配信のために端末識別情報等を収集する場合があります。\n\n初回起動時にApp Tracking Transparency（ATT）の許可確認が表示されます。許可しない場合でも本アプリの全機能をご利用いただけますが、表示される広告がパーソナライズされない場合があります。\n\nGoogle のプライバシーポリシー：policies.google.com/privacy'),
  ('第三者への提供',
   '収集した情報は、以下のサービスに送信されます：\n・Anthropic（AI解析）\n・Google Firebase（データ保存）\n・Google AdMob（広告配信）\n\nこれら以外の第三者に情報を販売・提供することはありません。'),
  ('データの保存と削除',
   'Firebaseに保存された解答データは、ユーザー自身がアプリ内から削除できます。アカウント機能はなく、端末を変えるとデータにはアクセスできなくなります。'),
  ('セキュリティ',
   'Firebase セキュリティルールにより、データへの不正アクセスを防止しています。ただし、インターネット上の完全なセキュリティを保証するものではありません。'),
  ('お問い合わせ',
   'プライバシーポリシーに関するご質問は、下記までご連絡ください。\n\nseadice.home@gmail.com'),
];

class _PrivacySection extends StatelessWidget {
  final String title;
  final String body;
  final Color lineColor;
  final bool compact;
  const _PrivacySection({
    required this.title,
    required this.body,
    this.lineColor = const Color(0xFF4F6EF7),
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: compact ? 20 : 36),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title,
              style: GoogleFonts.syne(fontSize: compact ? 14 : 18, fontWeight: FontWeight.w700, color: Colors.white, letterSpacing: -0.3).ja),
          const SizedBox(height: 10),
          Container(width: 32, height: 1, color: lineColor),
          const SizedBox(height: 12),
          Text(body,
              style: GoogleFonts.dmSans(fontSize: 14, color: Colors.white54, height: 1.85).ja),
        ],
      ),
    );
  }
}

// ──────────────────────────────────────────────
// App Privacy Pages
// ──────────────────────────────────────────────
final _appPrivacyData = <String, (String, Color, List<(String, String)>)>{
  'tikdog': (
    'TikDog',
    const Color(0xFFFF6B35),
    const [
      ('はじめに', 'このプライバシーポリシーは、SEADICE（以下「当方」）が提供するiOSアプリ「TikDog」における個人情報の取り扱いについて説明します。'),
      ('収集する情報', '本アプリは、氏名・メールアドレス・電話番号などの個人を特定できる情報を一切収集しません。動画の再生・いいね・報告などの操作データは匿名でFirebaseに保存されます。'),
      ('広告について', '本アプリはGoogle AdMob（Google LLC）による広告を表示します。AdMobは広告配信のために端末識別情報等を収集する場合があります。\n\n初回起動時にApp Tracking Transparency（ATT）の許可確認が表示されます。許可しない場合でも本アプリの全機能をご利用いただけますが、表示される広告がパーソナライズされない場合があります。\n\nGoogleのプライバシーポリシー：policies.google.com/privacy'),
      ('第三者への提供', '収集した情報は、以下のサービスに送信されます：\n・Google Firebase（動画データ管理）\n・Google AdMob（広告配信）\n\nこれら以外の第三者に情報を販売・提供することはありません。'),
      ('コンテンツについて', '本アプリに表示される動画はYouTubeのコンテンツです。各動画の著作権は元の動画投稿者に帰属します。不適切なコンテンツは報告機能から通報してください。'),
      ('お問い合わせ', 'プライバシーポリシーに関するご質問は、下記までご連絡ください。\n\nseadice.home@gmail.com'),
    ],
  ),
  'chozubora': (
    '超ズボラ日記',
    const Color(0xFFFF6B9D),
    const [
      ('はじめに', 'このプライバシーポリシーは、SEADICE（以下「当方」）が提供するiOSアプリ「超ズボラ日記」における個人情報の取り扱いについて説明します。'),
      ('収集する情報', '本アプリは、Googleアカウントでのログイン時にメールアドレスおよびGoogleカレンダーへのアクセス権限を取得します。氏名・電話番号・パスワードなどの情報は収集しません。\n\nユーザーが入力した日記テキストはAI整形のためにAnthropicのAPIへ送信され、整形後のテキストはGoogleカレンダーにのみ保存されます。日記データは当方のサーバーには保存されません。'),
      ('Googleアカウント連携', '本アプリはGoogle Sign-Inを使用してGoogleアカウントと連携します。取得するスコープはカレンダーへの書き込み権限（google.com/auth/calendar）のみです。\n\nGoogleのプライバシーポリシー：policies.google.com/privacy'),
      ('AI機能について', 'ユーザーが入力した日記テキストは、Anthropic社のClaude APIに送信され、文章の整形・改善に使用されます。送信されるのはテキストのみで、個人を特定できる情報は含まれません。\n\nAnthropicのプライバシーポリシー：anthropic.com/privacy'),
      ('広告について', '本アプリはGoogle AdMob（Google LLC）による広告を表示します。AdMobは広告配信のために端末識別情報等を収集する場合があります。\n\n初回起動時にApp Tracking Transparency（ATT）の許可確認が表示されます。許可しない場合でも本アプリの全機能をご利用いただけますが、表示される広告がパーソナライズされない場合があります。\n\nGoogleのプライバシーポリシー：policies.google.com/privacy'),
      ('通知について', '本アプリは毎日の日記記入をリマインドするためのローカル通知を送信します。通知の受信は端末の設定からいつでもオフにできます。'),
      ('第三者への提供', '収集した情報は、以下のサービスに送信されます：\n・Google（ログイン・カレンダー保存）\n・Anthropic（AI文章整形）\n・Google AdMob（広告配信）\n\nこれら以外の第三者に情報を販売・提供することはありません。'),
      ('データの削除', 'アプリをアンインストールすると端末上のデータはすべて削除されます。Googleカレンダーに保存された日記はGoogleカレンダーアプリから直接削除できます。'),
      ('お問い合わせ', 'プライバシーポリシーに関するご質問は、下記までご連絡ください。\n\nseadice.home@gmail.com'),
    ],
  ),
  'toite': (
    'TOITE',
    const Color(0xFF4F6EF7),
    const [
      ('はじめに', 'このプライバシーポリシーは、SEADICE（以下「当方」）が提供するiOSアプリ「TOITE」における個人情報の取り扱いについて説明します。'),
      ('収集する情報', '本アプリは、ユーザーが撮影またはアップロードした問題の画像をAI解析のために使用します。氏名・メールアドレス・電話番号などの個人を特定できる情報は収集しません。'),
      ('情報の利用目的', '取得した画像は、Anthropic社のClaude Vision APIに送信され、問題の解答・解説を生成するためにのみ使用されます。解答・解説テキストはGoogle Firebaseに保存され、ユーザー自身が履歴として参照できます。'),
      ('広告について', '本アプリはGoogle AdMob（Google LLC）による広告を表示します。AdMobは広告配信のために端末識別情報等を収集する場合があります。\n\n初回起動時にApp Tracking Transparency（ATT）の許可確認が表示されます。許可しない場合でも本アプリの全機能をご利用いただけますが、表示される広告がパーソナライズされない場合があります。\n\nGoogleのプライバシーポリシー：policies.google.com/privacy'),
      ('第三者への提供', '収集した情報は、以下のサービスに送信されます：\n・Anthropic（AI解析）\n・Google Firebase（データ保存）\n・Google AdMob（広告配信）\n\nこれら以外の第三者に情報を販売・提供することはありません。'),
      ('データの保存と削除', 'Firebaseに保存された解答データは、ユーザー自身がアプリ内から削除できます。アカウント機能はなく、端末を変えるとデータにはアクセスできなくなります。'),
      ('お問い合わせ', 'プライバシーポリシーに関するご質問は、下記までご連絡ください。\n\nseadice.home@gmail.com'),
    ],
  ),
  'piratasu': (
    'ピラミッド型タスク管理',
    const Color(0xFF00FFD1),
    const [
      ('収集する情報', '本アプリは、氏名・メールアドレス・電話番号などの個人を特定できる情報を一切収集しません。アプリの動作に必要なデータは端末内にのみ保存され、外部サーバーへの送信は行いません。'),
      ('端末内データの保存', 'ゴール・タスクのデータはお使いの端末内（ローカルストレージ）にのみ保存されます。アプリをアンインストールすると、すべてのデータが削除されます。'),
      ('マイク・音声認識の利用', '音声入力機能を使用する場合、音声データはApple標準の音声認識APIを通じて処理されます。SEADICEのサーバーに音声データが送信されることはありません。'),
      ('第三者への提供', '収集した情報を第三者に提供・販売することはありません。'),
    ],
  ),
  'kana-flip': (
    'Kana Flip',
    const Color(0xFFA78BFA),
    const [
      ('はじめに', 'このプライバシーポリシーは、SEADICE（以下「当方」）が提供するアプリ「Kana Flip」における個人情報の取り扱いについて説明します。'),
      ('収集する情報', '本アプリは、氏名・メールアドレス・電話番号などの個人を特定できる情報を一切収集しません。アプリの動作に必要なデータは端末内にのみ保存され、外部サーバーへの送信は行いません。'),
      ('端末内データの保存', '学習スコア・正解数などのデータはお使いの端末内（ローカルストレージ）にのみ保存されます。アプリをアンインストールすると、すべてのデータが削除されます。'),
      ('第三者への提供', '収集した情報を第三者に提供・販売することはありません。'),
      ('お問い合わせ', 'プライバシーポリシーに関するご質問は、下記までご連絡ください。\n\nseadice.home@gmail.com'),
    ],
  ),
  'breath': (
    'Breath',
    const Color(0xFF38BDF8),
    const [
      ('はじめに', 'このプライバシーポリシーは、SEADICE（以下「当方」）が提供するアプリ「Breath」における個人情報の取り扱いについて説明します。'),
      ('収集する情報', '本アプリは、個人情報を含むいかなるデータも収集・保存しません。すべての機能はインターネット接続なしで動作し、外部サーバーへのデータ送信は行いません。'),
      ('第三者への提供', '収集した情報を第三者に提供・販売することはありません。'),
      ('お問い合わせ', 'プライバシーポリシーに関するご質問は、下記までご連絡ください。\n\nseadice.home@gmail.com'),
    ],
  ),
  'palette-clock': (
    'Palette Clock',
    const Color(0xFFF472B6),
    const [
      ('はじめに', 'このプライバシーポリシーは、SEADICE（以下「当方」）が提供するアプリ「Palette Clock」における個人情報の取り扱いについて説明します。'),
      ('収集する情報', '本アプリは、個人情報を含むいかなるデータも収集・保存しません。すべての機能はインターネット接続なしで動作し、外部サーバーへのデータ送信は行いません。'),
      ('第三者への提供', '収集した情報を第三者に提供・販売することはありません。'),
      ('お問い合わせ', 'プライバシーポリシーに関するご質問は、下記までご連絡ください。\n\nseadice.home@gmail.com'),
    ],
  ),
  'one-tap-journal': (
    'One Tap Journal',
    const Color(0xFFF59E0B),
    const [
      ('はじめに', 'このプライバシーポリシーは、SEADICE（以下「当方」）が提供するアプリ「One Tap Journal」における個人情報の取り扱いについて説明します。'),
      ('収集する情報', '本アプリは、氏名・メールアドレス・電話番号などの個人を特定できる情報を一切収集しません。アプリの動作に必要なデータは端末内にのみ保存され、外部サーバーへの送信は行いません。'),
      ('端末内データの保存', '気分ログ・日記エントリなどのデータはお使いの端末内（ローカルストレージ）にのみ保存されます。アプリをアンインストールすると、すべてのデータが削除されます。'),
      ('第三者への提供', '収集した情報を第三者に提供・販売することはありません。'),
      ('お問い合わせ', 'プライバシーポリシーに関するご質問は、下記までご連絡ください。\n\nseadice.home@gmail.com'),
    ],
  ),
  'roll-and-go': (
    'Roll & Go',
    const Color(0xFFFF6B6B),
    const [
      ('はじめに', 'このプライバシーポリシーは、SEADICE（以下「当方」）が提供するアプリ「Roll & Go」における個人情報の取り扱いについて説明します。'),
      ('収集する情報', '本アプリは、個人情報を含むいかなるデータも収集・保存しません。すべての機能はインターネット接続なしで動作し、外部サーバーへのデータ送信は行いません。'),
      ('第三者への提供', '収集した情報を第三者に提供・販売することはありません。'),
      ('お問い合わせ', 'プライバシーポリシーに関するご質問は、下記までご連絡ください。\n\nseadice.home@gmail.com'),
    ],
  ),
  'life-is-rpg': (
    "Life's RPG",
    const Color(0xFFD4A017),
    const [
      ('はじめに', "このプライバシーポリシーは、SEADICE（以下「当方」）が提供するアプリ「Life's RPG」における個人情報の取り扱いについて説明します。"),
      ('収集する情報', '本アプリは、氏名・メールアドレス・電話番号などの個人を特定できる情報を一切収集しません。アプリの動作に必要なデータはすべてお使いの端末内（ローカルストレージ）にのみ保存され、外部サーバーへの送信は行いません。'),
      ('端末内データの保存', 'ゴール・クエスト・デイリーTODO・体調管理チェック・NOT TO DO・フォーカスセッションの記録、およびダンジョン進行データはすべてお使いの端末内にのみ保存されます。アプリをアンインストールすると、すべてのデータが削除されます。'),
      ('インターネット接続', '本アプリの全機能はインターネット接続なしで動作します。外部サーバーへのデータ送信は行いません。'),
      ('第三者への提供', '収集した情報を第三者に提供・販売することはありません。'),
      ('お問い合わせ', 'プライバシーポリシーに関するご質問は、下記までご連絡ください。\n\nseadice.home@gmail.com'),
    ],
  ),
  'drone-anki': (
    'ドローンCBT対策',
    const Color(0xFF3B82F6),
    const [
      ('はじめに', 'このプライバシーポリシーは、SEADICE（以下「当方」）が提供するアプリ「ドローンCBT対策」における個人情報の取り扱いについて説明します。'),
      ('収集する情報', '本アプリは、氏名・メールアドレス・電話番号などの個人を特定できる情報を一切収集しません。作成したカード・学習履歴はすべてお使いの端末内（ローカルストレージ）にのみ保存され、外部サーバーへの送信は行いません。'),
      ('端末内データの保存', '作成した暗記カードおよび学習履歴は、お使いの端末内にのみ保存されます。アプリを削除するとデータも削除されます。'),
      ('第三者への提供', '収集した情報を第三者に提供・販売することはありません。'),
      ('お問い合わせ', 'プライバシーポリシーに関するご質問は、下記までご連絡ください。\n\nseadice.home@gmail.com'),
    ],
  ),
  'rakuraku-anki': (
    '楽々暗記',
    const Color(0xFF00FFD1),
    const [
      ('はじめに', 'このプライバシーポリシーは、SEADICE（以下「当方」）が提供するアプリ「楽々暗記」における個人情報の取り扱いについて説明します。'),
      ('収集する情報', '本アプリは、氏名・メールアドレス・電話番号などの個人を特定できる情報を一切収集しません。作成したデッキ・カード・学習履歴はすべてお使いの端末内（ローカルストレージ）にのみ保存され、外部サーバーへの送信は行いません。'),
      ('AI カード生成機能について', '「AIでカードを生成」機能を使用する場合、入力されたテーマ（例：「TOEIC頻出動詞」）のテキストのみをAI処理のために送信します。個人を特定できる情報は送信されません。APIキーはサーバーサイドで管理されており、クライアントには露出しません。\n\nAI処理には Anthropic 社の API を使用しています。詳細は Anthropic 社のプライバシーポリシー（anthropic.com/privacy）をご参照ください。'),
      ('学習リマインダー通知', '学習リマインダーを有効にした場合、端末のローカル通知機能を使用します。通知に関するデータは端末内でのみ処理され、外部サーバーへの送信は行いません。'),
      ('データの管理', 'すべてのデータはお使いの端末にのみ保存されます。設定画面の「エクスポート」機能でいつでもバックアップできます。アプリをアンインストールすると、すべてのデータが削除されます。'),
      ('第三者への提供', '収集した情報を第三者に提供・販売することはありません。'),
      ('お問い合わせ', 'プライバシーポリシーに関するご質問は、下記までご連絡ください。\n\nseadice.home@gmail.com'),
    ],
  ),
};

// ─── 統合プライバシーポリシーページ (/privacy) ──────────────────────────────
class PrivacyPage extends StatelessWidget {
  const PrivacyPage({super.key});

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    final hPad = w > 800 ? w * 0.18 : w * 0.06;

    final allApps = _appPrivacyData.entries.toList();

    return Scaffold(
      backgroundColor: _bg,
      body: Stack(
        children: [
          SingleChildScrollView(
            child: Padding(
              padding: EdgeInsets.fromLTRB(hPad, 100, hPad, 80),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 720),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(children: [
                      Container(width: 24, height: 1, color: _accent),
                      const SizedBox(width: 10),
                      Text('SEADICE',
                          style: GoogleFonts.spaceMono(
                              fontSize: 11, letterSpacing: 3.5, color: _accent).ja),
                    ]),
                    const SizedBox(height: 12),
                    Text('プライバシーポリシー',
                        style: GoogleFonts.syne(
                            fontSize: 36, fontWeight: FontWeight.w800,
                            color: Colors.white, letterSpacing: -1).ja),
                    const SizedBox(height: 8),
                    Text('最終更新日：2026年6月6日',
                        style: GoogleFonts.spaceMono(
                            fontSize: 11, color: Colors.white30).ja),
                    const SizedBox(height: 48),

                    // 共通方針
                    _PrivacySection(
                      title: 'はじめに',
                      body: 'このプライバシーポリシーは、SEADICE（以下「当方」）が提供するすべてのアプリにおける個人情報の取り扱いについて説明します。',
                      lineColor: _accent,
                    ),
                    _PrivacySection(
                      title: '基本方針',
                      body: '当方のアプリは、氏名・メールアドレス・電話番号などの個人を特定できる情報を収集しません。各アプリのデータは原則としてお使いの端末内にのみ保存されます。一部アプリでのみ発生する特別な取り扱いについては、下記の各アプリのセクションをご覧ください。',
                      lineColor: _accent,
                    ),
                    _PrivacySection(
                      title: '第三者への提供',
                      body: '収集した情報を第三者に提供・販売することはありません。',
                      lineColor: _accent,
                    ),

                    // 区切り
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 32),
                      child: Row(children: [
                        Expanded(child: Container(height: 1, color: Colors.white10)),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: Text('各アプリの方針',
                              style: GoogleFonts.spaceMono(
                                  fontSize: 11, letterSpacing: 2, color: Colors.white30).ja),
                        ),
                        Expanded(child: Container(height: 1, color: Colors.white10)),
                      ]),
                    ),

                    // 各アプリ
                    ...allApps.map((entry) {
                      final (appName, accentColor, sections) = entry.value;
                      return _AppPrivacyBlock(
                        appName: appName,
                        accentColor: accentColor,
                        sections: sections,
                      );
                    }),

                    const SizedBox(height: 48),
                    _PrivacySection(
                      title: 'お問い合わせ',
                      body: 'プライバシーポリシーに関するご質問は、下記までご連絡ください。\n\nseadice.home@gmail.com',
                      lineColor: _accent,
                    ),
                    const SizedBox(height: 32),
                    MouseRegion(
                      cursor: SystemMouseCursors.click,
                      child: GestureDetector(
                        onTap: () =>
                            context.canPop() ? context.pop() : context.go('/'),
                        child: Row(mainAxisSize: MainAxisSize.min, children: [
                          Icon(Icons.arrow_back, color: _accent, size: 16),
                          const SizedBox(width: 8),
                          Text('Back',
                              style: GoogleFonts.spaceMono(
                                  fontSize: 11, letterSpacing: 1.5, color: _accent).ja),
                        ]),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            top: 0, left: 0, right: 0,
            child: ClipRect(
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
                child: Container(
                  height: 64,
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  decoration: BoxDecoration(
                    color: _bg.withValues(alpha: 0.72),
                    border: const Border(
                        bottom: BorderSide(color: Color(0x1A00FFD1))),
                  ),
                  child: Row(children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(6),
                      child: const _SpinningGear(size: 28),
                    ),
                    const SizedBox(width: 10),
                    Text('SEADICE',
                        style: GoogleFonts.spaceMono(
                            fontSize: 16, fontWeight: FontWeight.w700,
                            color: _accent, letterSpacing: 1.2).ja),
                  ]),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _AppPrivacyBlock extends StatefulWidget {
  final String appName;
  final Color accentColor;
  final List<(String, String)> sections;

  const _AppPrivacyBlock({
    required this.appName,
    required this.accentColor,
    required this.sections,
  });

  @override
  State<_AppPrivacyBlock> createState() => _AppPrivacyBlockState();
}

class _AppPrivacyBlockState extends State<_AppPrivacyBlock> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF0C0C1A),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: _expanded
              ? widget.accentColor.withValues(alpha: 0.3)
              : Colors.white.withValues(alpha: 0.06),
        ),
      ),
      child: Column(
        children: [
          InkWell(
            onTap: () => setState(() => _expanded = !_expanded),
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              child: Row(children: [
                Container(
                  width: 8, height: 8,
                  decoration: BoxDecoration(
                    color: widget.accentColor,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(widget.appName,
                      style: GoogleFonts.syne(
                          fontSize: 16, fontWeight: FontWeight.w700,
                          color: Colors.white).ja),
                ),
                Icon(
                  _expanded ? Icons.expand_less : Icons.expand_more,
                  color: Colors.white38,
                  size: 20,
                ),
              ]),
            ),
          ),
          if (_expanded)
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: widget.sections.map((s) => _PrivacySection(
                    title: s.$1, body: s.$2, lineColor: widget.accentColor,
                    compact: true)).toList(),
              ),
            ),
        ],
      ),
    );
  }
}

// ─── 既存の個別プライバシーページ (/privacy/:appId) ───────────────────────────
class AppPrivacyPage extends StatelessWidget {
  final String appId;
  const AppPrivacyPage({super.key, required this.appId});

  @override
  Widget build(BuildContext context) {
    final data = _appPrivacyData[appId];
    if (data == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) => context.go('/'));
      return const Scaffold(backgroundColor: _bg);
    }
    final (appName, accentColor, sections) = data;
    final w = MediaQuery.of(context).size.width;
    final hPad = w > 800 ? w * 0.18 : w * 0.06;

    return Scaffold(
      backgroundColor: _bg,
      body: Stack(
        children: [
          SingleChildScrollView(
            child: Padding(
              padding: EdgeInsets.fromLTRB(hPad, 100, hPad, 80),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 720),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(children: [
                      Container(width: 24, height: 1, color: accentColor),
                      const SizedBox(width: 10),
                      Text(appName.toUpperCase(),
                          style: GoogleFonts.spaceMono(
                              fontSize: 11, letterSpacing: 3.5, color: accentColor).ja),
                    ]),
                    const SizedBox(height: 12),
                    Text('プライバシーポリシー',
                        style: GoogleFonts.syne(
                            fontSize: 36, fontWeight: FontWeight.w800,
                            color: Colors.white, letterSpacing: -1).ja),
                    const SizedBox(height: 8),
                    Text('最終更新日：2026年5月26日',
                        style: GoogleFonts.spaceMono(
                            fontSize: 11, color: Colors.white30).ja),
                    const SizedBox(height: 48),
                    ...sections.map((s) => _PrivacySection(
                        title: s.$1, body: s.$2, lineColor: accentColor)),
                    const SizedBox(height: 48),
                    MouseRegion(
                      cursor: SystemMouseCursors.click,
                      child: GestureDetector(
                        onTap: () =>
                            context.canPop() ? context.pop() : context.go('/'),
                        child: Row(mainAxisSize: MainAxisSize.min, children: [
                          Icon(Icons.arrow_back, color: accentColor, size: 16),
                          const SizedBox(width: 8),
                          Text('Back',
                              style: GoogleFonts.spaceMono(
                                  fontSize: 11,
                                  letterSpacing: 1.5,
                                  color: accentColor).ja),
                        ]),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            top: 0, left: 0, right: 0,
            child: ClipRect(
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
                child: Container(
                  height: 64,
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  decoration: BoxDecoration(
                    color: _bg.withValues(alpha: 0.72),
                    border: const Border(
                        bottom: BorderSide(color: Color(0x1A00FFD1))),
                  ),
                  child: Row(children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(6),
                      child: const _SpinningGear(size: 28),
                    ),
                    const SizedBox(width: 10),
                    Text('SEADICE',
                        style: GoogleFonts.spaceMono(
                            fontSize: 16, fontWeight: FontWeight.w700,
                            color: _accent, letterSpacing: 1.2).ja),
                  ]),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ──────────────────────────────────────────────
// 言い訳ジェネレーター Mini
// ──────────────────────────────────────────────
const _excuseSituations = [
  '遅刻',
  '締め切り遅れ',
  '欠席・無断欠勤',
  '宿題・課題忘れ',
  '返信が遅れた',
  '約束をすっぽかした',
  '失敗・ミスをした',
];

const _excuseAccent = Color(0xFFA78BFA);
const _functionUrl = 'https://generateexcuse-3cevhzldhq-an.a.run.app';

class ExcuseGeneratorMini extends StatefulWidget {
  const ExcuseGeneratorMini({super.key});
  @override
  State<ExcuseGeneratorMini> createState() => _ExcuseGeneratorMiniState();
}

class _ExcuseGeneratorMiniState extends State<ExcuseGeneratorMini> {
  String _situation = _excuseSituations[0];
  final _detailCtrl = TextEditingController();
  String? _excuse;
  bool _loading = false;
  String? _error;
  int _usedToday = 0;
  static const _maxPerDay = 10;
  static const _prefKey = 'excuse_usage';

  @override
  void initState() {
    super.initState();
    _loadUsage();
  }

  Future<void> _loadUsage() async {
    final prefs = await SharedPreferences.getInstance();
    final today = DateTime.now().toIso8601String().substring(0, 10);
    final stored = prefs.getString(_prefKey) ?? '';
    final parts = stored.split(',');
    if (parts.length == 2 && parts[0] == today) {
      setState(() => _usedToday = int.tryParse(parts[1]) ?? 0);
    }
  }

  Future<void> _saveUsage() async {
    final prefs = await SharedPreferences.getInstance();
    final today = DateTime.now().toIso8601String().substring(0, 10);
    await prefs.setString(_prefKey, '$today,$_usedToday');
  }

  @override
  void dispose() {
    _detailCtrl.dispose();
    super.dispose();
  }

  Future<void> _generate() async {
    if (_usedToday >= _maxPerDay) {
      setState(() => _error = '本日の使用回数（$_maxPerDay 回）に達しました。また明日どうぞ。');
      return;
    }
    setState(() { _loading = true; _error = null; _excuse = null; });
    try {
      final res = await http.post(
        Uri.parse(_functionUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'situation': _situation,
          'detail': _detailCtrl.text.trim(),
        }),
      );
      final body = jsonDecode(res.body) as Map<String, dynamic>;
      if (res.statusCode == 200) {
        setState(() {
          _excuse = body['excuse'] as String;
          _usedToday++;
        });
        await _saveUsage();
      } else {
        setState(() => _error = body['error']?.toString() ?? 'エラーが発生しました');
      }
    } catch (e) {
      setState(() => _error = 'ネットワークエラー: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('シチュエーション',
              style: GoogleFonts.spaceMono(
                  fontSize: 10, letterSpacing: 2, color: _excuseAccent).ja),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _excuseSituations.map((s) {
              final active = s == _situation;
              return GestureDetector(
                onTap: () => setState(() { _situation = s; _excuse = null; }),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 150),
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: active
                        ? _excuseAccent.withValues(alpha: 0.2)
                        : Colors.white.withValues(alpha: 0.05),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: active
                          ? _excuseAccent
                          : Colors.white.withValues(alpha: 0.15),
                    ),
                  ),
                  child: Text(s,
                      style: GoogleFonts.dmSans(
                          fontSize: 12,
                          color: active ? _excuseAccent : Colors.white60).ja),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _detailCtrl,
            style: GoogleFonts.dmSans(fontSize: 13, color: Colors.white).ja,
            decoration: InputDecoration(
              hintText: '補足（任意）例: 上司へ・朝の会議',
              hintStyle: GoogleFonts.dmSans(fontSize: 12, color: Colors.white30).ja,
              filled: true,
              fillColor: Colors.white.withValues(alpha: 0.05),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: const BorderSide(color: _excuseAccent),
              ),
              contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: GestureDetector(
              onTap: _loading ? null : _generate,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 150),
                padding: const EdgeInsets.symmetric(vertical: 14),
                decoration: BoxDecoration(
                  color: _excuseAccent.withValues(alpha: _loading ? 0.1 : 0.15),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: _excuseAccent.withValues(alpha: 0.6)),
                ),
                child: Center(
                  child: _loading
                      ? const SizedBox(
                          width: 18, height: 18,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: _excuseAccent))
                      : Text('言い訳を生成',
                          style: GoogleFonts.syne(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: _excuseAccent).ja),
                ),
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '本日 $_usedToday / $_maxPerDay 回使用済み',
            style: GoogleFonts.spaceMono(
                fontSize: 10,
                color: _usedToday >= _maxPerDay
                    ? Colors.redAccent
                    : Colors.white38).ja,
          ),
          if (_error != null) ...[
            const SizedBox(height: 12),
            Text(_error!,
                style: GoogleFonts.dmSans(fontSize: 12, color: Colors.redAccent).ja),
          ],
          if (_excuse != null) ...[
            const SizedBox(height: 20),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: _excuseAccent.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _excuseAccent.withValues(alpha: 0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('生成された言い訳',
                      style: GoogleFonts.spaceMono(
                          fontSize: 9, letterSpacing: 2, color: _excuseAccent).ja),
                  const SizedBox(height: 10),
                  Text(_excuse!,
                      style: GoogleFonts.dmSans(
                          fontSize: 14, color: Colors.white, height: 1.7).ja),
                  const SizedBox(height: 12),
                  GestureDetector(
                    onTap: () {
                      Clipboard.setData(ClipboardData(text: _excuse!));
                      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                        content: Text('コピーしました',
                            style: GoogleFonts.dmSans(fontSize: 13).ja),
                        duration: const Duration(seconds: 2),
                        backgroundColor: _excuseAccent.withValues(alpha: 0.8),
                      ));
                    },
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.copy, size: 14, color: _excuseAccent),
                        const SizedBox(width: 6),
                        Text('コピー',
                            style: GoogleFonts.spaceMono(
                                fontSize: 10,
                                letterSpacing: 1,
                                color: _excuseAccent).ja),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

// ──────────────────────────────────────────────
// Order Page（受注ページ）
// ──────────────────────────────────────────────
class OrderPage extends StatelessWidget {
  const OrderPage({super.key});

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    final hPad = w > 800 ? w * 0.12 : w * 0.06;

    return Scaffold(
      backgroundColor: _bg,
      body: Stack(
        children: [
          SingleChildScrollView(
            child: Padding(
              padding: EdgeInsets.fromLTRB(hPad, 100, hPad, 80),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 800),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(children: [
                      Container(width: 8, height: 8,
                          decoration: const BoxDecoration(
                              color: _accent, shape: BoxShape.circle)),
                      const SizedBox(width: 10),
                      Text('受注受付中',
                          style: GoogleFonts.spaceMono(
                              fontSize: 11, letterSpacing: 3, color: _accent).ja),
                    ]),
                    const SizedBox(height: 16),
                    Text('あなただけの\n特別なアプリを',
                        style: GoogleFonts.syne(
                            fontSize: w > 600 ? 52 : w > 400 ? 38 : 30,
                            fontWeight: FontWeight.w800,
                            color: Colors.white,
                            height: 1.1,
                            letterSpacing: -1).ja),
                    const SizedBox(height: 16),
                    Text('「こんなツールがほしい」「あのアイデアをアプリにしたい」——\nそのひらめきを、世界にひとつだけのWebアプリへ。',
                        style: GoogleFonts.dmSans(
                            fontSize: 15, color: Colors.white54, height: 1.8).ja),
                    const SizedBox(height: 56),

                    // サービス内容
                    _OrderSection(
                      label: 'SERVICE',
                      title: 'できること',
                      children: const [
                        _ServiceItem(icon: Icons.language_rounded, title: 'オーダーメイド Web アプリ',
                            desc: 'Flutter + Firebase で0から設計・開発。デプロイまで丸ごと一貫対応。スマホでもPCでも快適に動きます。'),
                        _ServiceItem(icon: Icons.smart_toy_outlined, title: 'AI 機能の実装',
                            desc: 'ChatGPT・Claude などの最新AIを搭載した最強のアプリへ。'),
                        _ServiceItem(icon: Icons.bolt_rounded, title: 'ツール・業務自動化',
                            desc: '毎日の手作業をWebで自動化。「これ、アプリにしたい」と思った瞬間が始まりのサイン。'),
                        _ServiceItem(icon: Icons.brush_rounded, title: 'UI / UX デザイン',
                            desc: 'こだわりたい方はここへ。どんなデザインでも対応可能。'),
                      ],
                    ),
                    const SizedBox(height: 48),

                    // 料金
                    _OrderSection(
                      label: 'PRICING',
                      title: '月額0円Webアプリ',
                      children: [
                        Container(
                          margin: const EdgeInsets.only(bottom: 20),
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 12),
                          decoration: BoxDecoration(
                            color: _accent.withValues(alpha: 0.06),
                            border: Border(
                              left: BorderSide(
                                  color: _accent.withValues(alpha: 0.6),
                                  width: 3),
                            ),
                          ),
                          child: Text(
                            '初期費用のみ'
                            '個人使用に限定'
                            '※AI機能付きのプランは1日の使用回数に上限を設けます',
                            style: GoogleFonts.dmSans(
                                fontSize: 13,
                                color: Colors.white60,
                                height: 1.7).ja,
                          ),
                        ),
                        const _PricingItem(plan: 'ベーシック', price: '¥3,000',
                            desc: 'ログイン・クラウド保存あり。端末を変えてもキャッシュを消してもデータは消えません。外部API連携なし。シンプルなアプリを確実に使い続けたい方へ。'),
                        const _PricingItem(plan: 'スタンダード', price: '¥5,000',
                            desc: 'ベーシックの全機能＋外部API連携。AIや天気・地図など外部サービスをつなぎたいときはこちら。AIは1日の使用回数に上限を設定。'),
                        const SizedBox(height: 16),
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                          decoration: BoxDecoration(
                            color: _accent.withValues(alpha: 0.05),
                            border: Border.all(color: _accent.withValues(alpha: 0.3)),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('全プラン：納品後1ヶ月無料サポート',
                                  style: GoogleFonts.syne(
                                      fontSize: 13, fontWeight: FontWeight.w700,
                                      color: _accent).ja),
                              const SizedBox(height: 4),
                              Text('バグ修正はいつでも無償。改善・機能追加は1ヶ月間無償、期間後は1回¥1,000。',
                                  style: GoogleFonts.dmSans(
                                      fontSize: 12, color: Colors.white38).ja),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 48),

                    // 流れ
                    _OrderSection(
                      label: 'FLOW',
                      title: 'ご依頼の流れ',
                      children: const [
                        _FlowItem(step: '01', title: '相談・ヒアリングと見積もり',
                            desc: 'まずはメールで。「こんなもの作りたい」くらいでOK。要件を一緒に整理し、費用と期間をご提示。'),
                        _FlowItem(step: '02', title: 'サンプルアプリ公開',
                            desc: '最初のバージョンを実際に触れる状態で公開。使ってみて「続けたい」と思えば次のステップへ。納得できなければここで終了でもOK。'),
                        _FlowItem(step: '03', title: '料金お支払い',
                            desc: '継続を決めていただいた時点でお支払いをお願いします。先払いなし・納得してからが基本。'),
                        _FlowItem(step: '04', title: '修正・改善を経て納品',
                            desc: 'フィードバックをもとに磨き込み、完成したらすぐ使える状態でお渡し。公開・デプロイも一貫対応。'),
                      ],
                    ),
                    const SizedBox(height: 56),

                    // FAQ
                    _OrderSection(
                      label: 'FAQ',
                      title: 'よくある質問',
                      children: const [
                        _FaqItem(
                          q: 'どんなアプリが作れますか？',
                          a: '個人が日常で使うWebアプリならほぼなんでも。読書記録・習慣トラッカー・推し活ノート・家計簿・スケジュール管理など。',
                        ),
                        _FaqItem(
                          q: 'アイデアがぼんやりしていても大丈夫ですか？',
                          a: '「こんな感じのものがほしい」くらいでも作成します。',
                        ),
                        _FaqItem(
                          q: '納期はどのくらいですか？',
                          a: 'ベーシック・スタンダードともに1週間以内が目安。要件によって前後あり。',
                        ),
                        _FaqItem(
                          q: '途中で要件が変わっても大丈夫ですか？',
                          a: '開発中のフィードバックは歓迎。ただし大幅な仕様変更は別途相談。バグ修正はいつでも無償。改善・機能追加は1ヶ月間無償、期間後は1回¥1,000。',
                        ),
                        _FaqItem(
                          q: 'スマホでも使えますか？',
                          a: '全プランでスマホ・PC両対応（レスポンシブ）。ブラウザで開くWebアプリなので、App Store・Google Playへのリリースは対象外。',
                        ),
                        _FaqItem(
                          q: '使用している技術スタックは？',
                          a: 'Flutter（フロントエンド）+ Firebase（バックエンド・ホスティング）を基本構成として使用。',
                        ),
                      ],
                    ),
                    const SizedBox(height: 56),

                    // CTA
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(32),
                      decoration: BoxDecoration(
                        color: _accent.withValues(alpha: 0.06),
                        border: Border.all(color: _accent.withValues(alpha: 0.25)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('アイデアを、形へ。',
                              style: GoogleFonts.syne(
                                  fontSize: 22, fontWeight: FontWeight.w800,
                                  color: Colors.white, letterSpacing: -0.5).ja),
                          const SizedBox(height: 8),
                          Text('既存のアプリで満足できないあなたへ、あなた専用のアプリを。\nぼんやりしたアイデアで大丈夫。見積もりは無料。',
                              style: GoogleFonts.dmSans(
                                  fontSize: 14, color: Colors.white54, height: 1.7).ja),
                        ],
                      ),
                    ),
                    const SizedBox(height: 48),
                    GestureDetector(
                      onTap: () => context.canPop()
                          ? context.pop()
                          : context.go('/'),
                      child: Row(mainAxisSize: MainAxisSize.min, children: [
                        const Icon(Icons.arrow_back, color: _accent, size: 16),
                        const SizedBox(width: 8),
                        Text('Back',
                            style: GoogleFonts.spaceMono(
                                fontSize: 11,
                                letterSpacing: 1.5,
                                color: _accent).ja),
                      ]),
                    ),
                  ],
                ),
              ),
            ),
          ),
          // Navbar
          Positioned(
            top: 0, left: 0, right: 0,
            child: ClipRect(
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
                child: Container(
                  height: 64,
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  decoration: BoxDecoration(
                    color: _bg.withValues(alpha: 0.72),
                    border: const Border(
                        bottom: BorderSide(color: Color(0x1A00FFD1))),
                  ),
                  child: Row(children: [
                    const _SpinningGear(size: 28),
                    const SizedBox(width: 10),
                    Text('SEADICE',
                        style: GoogleFonts.spaceMono(
                            fontSize: 16, fontWeight: FontWeight.w700,
                            color: _accent, letterSpacing: 1.2).ja),
                  ]),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _OrderSection extends StatelessWidget {
  final String label;
  final String title;
  final List<Widget> children;
  const _OrderSection(
      {required this.label, required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(children: [
          Container(width: 24, height: 1, color: _accent),
          const SizedBox(width: 10),
          Text(label,
              style: GoogleFonts.spaceMono(
                  fontSize: 11, letterSpacing: 3.5, color: _accent).ja),
        ]),
        const SizedBox(height: 12),
        Text(title,
            style: GoogleFonts.syne(
                fontSize: 28, fontWeight: FontWeight.w800,
                color: Colors.white, letterSpacing: -0.5).ja),
        const SizedBox(height: 24),
        ...children,
      ],
    );
  }
}

class _ServiceItem extends StatelessWidget {
  final IconData icon;
  final String title, desc;
  const _ServiceItem(
      {required this.icon, required this.title, required this.desc});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 22, color: _accent),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: GoogleFonts.syne(
                        fontSize: 15, fontWeight: FontWeight.w700,
                        color: Colors.white).ja),
                const SizedBox(height: 4),
                Text(desc,
                    style: GoogleFonts.dmSans(
                        fontSize: 13, color: Colors.white54, height: 1.7).ja),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PricingItem extends StatelessWidget {
  final String plan, price, desc;
  const _PricingItem(
      {required this.plan, required this.price, required this.desc});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.03),
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(plan,
                    style: GoogleFonts.syne(
                        fontSize: 15, fontWeight: FontWeight.w700,
                        color: Colors.white).ja),
                const SizedBox(height: 4),
                Text(desc,
                    style: GoogleFonts.dmSans(
                        fontSize: 13, color: Colors.white38).ja),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(price,
                  style: GoogleFonts.spaceMono(
                      fontSize: 14, color: _accent, letterSpacing: 1).ja),
              const SizedBox(height: 4),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: _accent.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(3),
                ),
                child: Text('月額 ¥0',
                    style: GoogleFonts.spaceMono(
                        fontSize: 9, color: _accent, letterSpacing: 0.5).ja),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _FaqItem extends StatelessWidget {
  final String q, a;
  const _FaqItem({required this.q, required this.a});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.02),
        border: Border.all(color: Colors.white.withValues(alpha: 0.07)),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('Q. ', style: GoogleFonts.spaceMono(
                fontSize: 11, color: _accent, fontWeight: FontWeight.w700).ja),
            Expanded(child: Text(q, style: GoogleFonts.syne(
                fontSize: 14, fontWeight: FontWeight.w700,
                color: Colors.white).ja)),
          ]),
          const SizedBox(height: 10),
          Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('A. ', style: GoogleFonts.spaceMono(
                fontSize: 11, color: Colors.white30).ja),
            Expanded(child: Text(a, style: GoogleFonts.dmSans(
                fontSize: 13, color: Colors.white54, height: 1.7).ja)),
          ]),
        ],
      ),
    );
  }
}

class _FlowItem extends StatelessWidget {
  final String step, title, desc;
  const _FlowItem(
      {required this.step, required this.title, required this.desc});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(step,
              style: GoogleFonts.spaceMono(
                  fontSize: 20, fontWeight: FontWeight.w700,
                  color: _accent.withValues(alpha: 0.4)).ja),
          const SizedBox(width: 20),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: GoogleFonts.syne(
                        fontSize: 15, fontWeight: FontWeight.w700,
                        color: Colors.white).ja),
                const SizedBox(height: 4),
                Text(desc,
                    style: GoogleFonts.dmSans(
                        fontSize: 13, color: Colors.white54, height: 1.7).ja),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
