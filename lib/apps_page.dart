import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

/// ===============================
/// Model
/// ===============================
class AppItem {
  final String appId;
  final String title;
  final String cardImage;
  final String web;
  final String google;
  final String ios;

  AppItem({
    required this.appId,
    required this.title,
    required this.cardImage,
    required this.web,
    required this.google,
    required this.ios,
  });

  factory AppItem.fromJson(Map<String, dynamic> json) {
    return AppItem(
      appId: json['appId'],
      title: json['title'],
      cardImage: json['icon'], // ← 将来 cardImage に分離してOK
      web: json['links']['web'] ?? '',
      google: json['links']['google'] ?? '',
      ios: json['links']['ios'] ?? '',
    );
  }
}

/// ===============================
/// Apps Page
/// ===============================
class AppsPage extends StatefulWidget {
  const AppsPage({super.key});

  @override
  State<AppsPage> createState() => _AppsPageState();
}

class _AppsPageState extends State<AppsPage> {
  late Future<List<AppItem>> _appsFuture;

  @override
  void initState() {
    super.initState();
    _appsFuture = _loadApps();
  }

  Future<List<AppItem>> _loadApps() async {
    final raw = await rootBundle.loadString('assets/data/apps.json');
    final decoded = jsonDecode(raw) as Map<String, dynamic>;
    return (decoded['apps'] as List).map((e) => AppItem.fromJson(e)).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0F0F),
      appBar: AppBar(
        title: const Text('Apps'),
        backgroundColor: const Color(0xFF0F0F0F),
        elevation: 0,
      ),
      body: FutureBuilder<List<AppItem>>(
        future: _appsFuture,
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return const Center(child: CircularProgressIndicator());
          }

          final apps = snapshot.data!;

          return LayoutBuilder(
            builder: (context, constraints) {
              final w = constraints.maxWidth;
              final columns = w < 600
                  ? 1
                  : w < 900
                  ? 2
                  : w < 1200
                  ? 3
                  : 4;

              return GridView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: apps.length,
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: columns,
                  mainAxisSpacing: 16,
                  crossAxisSpacing: 16,
                  childAspectRatio: 1.0, // ★ 正方形
                ),
                itemBuilder: (context, index) {
                  return _AppCard(app: apps[index], width: w);
                },
              );
            },
          );
        },
      ),
    );
  }
}

/// ===============================
/// App Card（Square + Overlay）
/// ===============================
class _AppCard extends StatefulWidget {
  final AppItem app;
  final double width;
  const _AppCard({required this.app, required this.width});

  @override
  State<_AppCard> createState() => _AppCardState();
}

class _AppCardState extends State<_AppCard> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final isPc = widget.width >= 900;
    final titleSize = widget.width < 600
        ? 25.0
        : widget.width < 900
        ? 22.0
        : 20.0;

    return MouseRegion(
      onEnter: (_) => isPc ? setState(() => _hover = true) : null,
      onExit: (_) => isPc ? setState(() => _hover = false) : null,
      child: GestureDetector(
        onTap: () => context.go('/apps/${widget.app.appId}'),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          transform: _hover
              ? (Matrix4.identity()..translate(0.0, -6.0))
              : Matrix4.identity(),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            boxShadow: _hover
                ? [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.45),
                      blurRadius: 18,
                      offset: const Offset(0, 10),
                    ),
                  ]
                : [],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Stack(
              children: [
                /// 背景画像
                Positioned.fill(
                  child: Image.asset(widget.app.cardImage, fit: BoxFit.cover),
                ),

                /// グラデーション（下）
                Positioned.fill(
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.bottomCenter,
                        end: Alignment.topCenter,
                        colors: [
                          _hover
                              ? const Color(0xEE0F0F0F)
                              : const Color(0xCC0F0F0F),
                          const Color(0x660F0F0F),
                          const Color(0x00000000),
                        ],
                      ),
                    ),
                  ),
                ),

                /// タイトル + ボタン（画像の上）
                Positioned(
                  left: 12,
                  right: 12,
                  bottom: 12,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.app.title,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: titleSize,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          _StoreButton(
                            icon: Icons.language,
                            url: widget.app.web,
                          ),
                          _StoreButton(
                            icon: Icons.android,
                            url: widget.app.google,
                          ),
                          _StoreButton(icon: Icons.apple, url: widget.app.ios),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// ===============================
/// Store Button（Hover + Disabled）
// ===============================
class _StoreButton extends StatefulWidget {
  final IconData icon;
  final String url;
  const _StoreButton({required this.icon, required this.url});

  @override
  State<_StoreButton> createState() => _StoreButtonState();
}

class _StoreButtonState extends State<_StoreButton> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final enabled = widget.url.isNotEmpty;

    final color = !enabled
        ? const Color(0xFF555555)
        : _hover
        ? Colors.white
        : const Color(0xFF10A37F);

    return MouseRegion(
      onEnter: (_) => enabled ? setState(() => _hover = true) : null,
      onExit: (_) => enabled ? setState(() => _hover = false) : null,
      child: GestureDetector(
        onTap: enabled
            ? () async {
                final uri = Uri.parse(widget.url);
                if (await canLaunchUrl(uri)) {
                  await launchUrl(uri, mode: LaunchMode.externalApplication);
                }
              }
            : null,
        child: Container(
          margin: const EdgeInsets.only(right: 8),
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            border: Border.all(
              color: enabled
                  ? const Color(0xFF2A2A2A)
                  : const Color(0xFF1A1A1A),
            ),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(widget.icon, size: 18, color: color),
        ),
      ),
    );
  }
}
