import 'dart:async';
import 'package:flutter/material.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage>
    with SingleTickerProviderStateMixin {
  int _index = 0;
  Timer? _timer;

  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  final List<_HeroTextItem> _texts = const [
    _HeroTextItem(
      title: 'AI, Naturally',
      subtitle: 'Small, useful, fun apps for everyday moments.',
    ),
    _HeroTextItem(
      title: 'Intuitive',
      subtitle: 'Games, utilities, and learning tools — all in one place.',
    ),
    _HeroTextItem(
      title: 'Built around you',
      subtitle: 'Explore what fits your style and your day.',
    ),
  ];

  @override
  void initState() {
    super.initState();

    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );

    _fadeAnimation = CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOut,
    );

    _fadeController.forward();

    _timer = Timer.periodic(const Duration(seconds: 4), (_) async {
      await _fadeController.reverse();
      if (!mounted) return;
      setState(() {
        _index = (_index + 1) % _texts.length;
      });
      _fadeController.forward();
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0F0F),

      /// ===============================
      /// AppBar
      /// ===============================
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F0F0F),
        elevation: 0,
        titleSpacing: 12,
        title: Row(
          children: [
            Image.asset('assets/logo/seadice_icon.png', width: 28, height: 28),
            const SizedBox(width: 8),
            const Text(
              'SEADICE',
              style: TextStyle(fontWeight: FontWeight.w600, letterSpacing: 0.6),
            ),
          ],
        ),
      ),

      /// ===============================
      /// Body
      /// ===============================
      body: Stack(
        children: [
          /// ゆっくり動く背景画像
          const _MovingBackground(),

          /// Dark overlay（可読性）
          Positioned.fill(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.bottomCenter,
                  end: Alignment.topCenter,
                  colors: [
                    Color(0xEE0F0F0F),
                    Color(0x880F0F0F),
                    Color(0x200F0F0F),
                  ],
                ),
              ),
            ),
          ),

          /// 左下テキスト（フェード切替）
          Positioned(
            left: 24,
            right: 24,
            bottom: 56,
            child: FadeTransition(
              opacity: _fadeAnimation,
              child: _HeroText(
                title: _texts[_index].title,
                subtitle: _texts[_index].subtitle,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// ===============================
/// 背景をゆっくり動かす
/// ===============================
class _MovingBackground extends StatefulWidget {
  const _MovingBackground();

  @override
  State<_MovingBackground> createState() => _MovingBackgroundState();
}

class _MovingBackgroundState extends State<_MovingBackground> {
  bool _move = false;

  @override
  void initState() {
    super.initState();
    Future.delayed(Duration.zero, () {
      if (mounted) {
        setState(() => _move = true);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedPositioned(
      duration: const Duration(seconds: 25),
      curve: Curves.linear,
      top: 0,
      bottom: 0,
      left: _move ? -40 : 0,
      right: _move ? 0 : -40,
      child: Image.asset('assets/hero/hero_1.jpg', fit: BoxFit.cover),
    );
  }
}

/// ===============================
/// Heroテキスト
/// ===============================
class _HeroText extends StatelessWidget {
  final String title;
  final String subtitle;

  const _HeroText({required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 28,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.4,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          subtitle,
          style: const TextStyle(
            color: Color(0xFFB0B0B0),
            fontSize: 14,
            height: 1.4,
          ),
        ),
      ],
    );
  }
}

/// ===============================
/// Heroテキストデータ
/// ===============================
class _HeroTextItem {
  final String title;
  final String subtitle;

  const _HeroTextItem({required this.title, required this.subtitle});
}
