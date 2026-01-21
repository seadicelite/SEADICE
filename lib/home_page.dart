import 'package:flutter/material.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scale;
  late Animation<Offset> _offset;

  @override
  void initState() {
    super.initState();

    // 15秒で往復（ゆっくり）
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 15),
    )..repeat(reverse: true);

    // ゆっくりズーム
    _scale = Tween<double>(
      begin: 1.0,
      end: 1.05,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.linear));

    // わずかに斜め移動（動画っぽさ）
    _offset = Tween<Offset>(
      begin: const Offset(-0.02, 0.02),
      end: const Offset(0.02, -0.02),
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.linear));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0F0F),

      // ===============================
      // AppBar（ロゴ＋テキスト）
      // ===============================
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

      // ===============================
      // Hero
      // ===============================
      body: Stack(
        children: [
          /// 背景（1枚画像＋超スローアニメ）
          Positioned.fill(
            child: AnimatedBuilder(
              animation: _controller,
              builder: (context, child) {
                return FractionalTranslation(
                  translation: _offset.value,
                  child: Transform.scale(scale: _scale.value, child: child),
                );
              },
              child: Image.asset('assets/hero/hero_1.jpg', fit: BoxFit.cover),
            ),
          ),

          /// 黒グラデーション（文字の可読性）
          Positioned.fill(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.bottomCenter,
                  end: Alignment.topCenter,
                  colors: [
                    Color(0xDD0F0F0F),
                    Color(0x800F0F0F),
                    Color(0x200F0F0F),
                  ],
                ),
              ),
            ),
          ),

          /// ===============================
          /// テキスト & CTA
          /// ===============================
          Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text(
                    'Welcome to SEADICE',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 36,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.6,
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Try one. Find your favorite.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Color(0xFFB0B0B0), fontSize: 16),
                  ),
                  const SizedBox(height: 36),

                  /// CTA
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF10A37F),
                      foregroundColor: Colors.white,
                      elevation: 0,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 36,
                        vertical: 14,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(28),
                      ),
                    ),
                    onPressed: () {
                      // RootPage側で Apps タブに切り替える想定
                    },
                    child: const Text(
                      'Browse Apps',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
