import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';

/// ===============================
/// Model
/// ===============================
class AppItem {
  final String appId;
  final String name;
  final String category;
  final String oneLine;
  final String icon;
  final Map<String, dynamic> links;

  AppItem({
    required this.appId,
    required this.name,
    required this.category,
    required this.oneLine,
    required this.icon,
    required this.links,
  });

  factory AppItem.fromJson(Map<String, dynamic> json) {
    return AppItem(
      appId: json['appId'],
      name: json['name'],
      category: json['category'],
      oneLine: json['oneLine'],
      icon: json['icon'] ?? '',
      links: json['links'] ?? {},
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
  String _filter = 'all'; // all / game / utility / learning

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
      body: Column(
        children: [
          /// フィルタ（任意・軽い）
          _CategoryFilter(
            current: _filter,
            onChanged: (v) => setState(() => _filter = v),
          ),

          /// 一覧
          Expanded(
            child: FutureBuilder<List<AppItem>>(
              future: _appsFuture,
              builder: (context, snapshot) {
                if (!snapshot.hasData) {
                  return const Center(child: CircularProgressIndicator());
                }

                final apps = snapshot.data!
                    .where((a) => _filter == 'all' || a.category == _filter)
                    .toList();

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
                      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: columns,
                        mainAxisSpacing: 16,
                        crossAxisSpacing: 16,
                        childAspectRatio: 0.72, // ストア感
                      ),
                      itemCount: apps.length,
                      itemBuilder: (context, index) {
                        return _StoreStyleAppCard(app: apps[index]);
                      },
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

/// ===============================
/// Category Filter (Chip)
/// ===============================
class _CategoryFilter extends StatelessWidget {
  final String current;
  final ValueChanged<String> onChanged;
  const _CategoryFilter({required this.current, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 8),
      child: Row(
        children: [
          _chip('all', 'All'),
          _chip('game', 'Game'),
          _chip('utility', 'Utility'),
          _chip('learning', 'Learning'),
        ],
      ),
    );
  }

  Widget _chip(String value, String label) {
    final selected = current == value;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ChoiceChip(
        label: Text(label),
        selected: selected,
        onSelected: (_) => onChanged(value),
        selectedColor: const Color(0xFF10A37F),
        backgroundColor: const Color(0xFF1E1E1E),
        labelStyle: TextStyle(
          color: selected ? Colors.white : const Color(0xFFB0B0B0),
        ),
        side: const BorderSide(color: Color(0xFF2A2A2A)),
      ),
    );
  }
}

/// ===============================
/// Store Style Card (Hover対応)
/// ===============================
class _StoreStyleAppCard extends StatefulWidget {
  final AppItem app;
  const _StoreStyleAppCard({required this.app});

  @override
  State<_StoreStyleAppCard> createState() => _StoreStyleAppCardState();
}

class _StoreStyleAppCardState extends State<_StoreStyleAppCard> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 160),
        curve: Curves.easeOut,
        transform: _hover ? (Matrix4.identity()..translate(0.0, -4.0)) : null,
        decoration: BoxDecoration(
          color: const Color(0xFF1E1E1E),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: _hover ? const Color(0xFF3A3A3A) : const Color(0xFF2A2A2A),
          ),
        ),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () => context.go('/apps/${widget.app.appId}'),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              /// アイコン（正方形）
              ClipRRect(
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(16),
                ),
                child: AspectRatio(
                  aspectRatio: 1,
                  child: widget.app.icon.isEmpty
                      ? Container(
                          color: const Color(0xFF2A2A2A),
                          child: const Icon(
                            Icons.apps,
                            size: 48,
                            color: Colors.white,
                          ),
                        )
                      : Image.asset(widget.app.icon, fit: BoxFit.cover),
                ),
              ),

              /// テキスト
              Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.app.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.app.oneLine,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: Color(0xFFB0B0B0),
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 6,
                      children: [
                        if (widget.app.links['web']?.isNotEmpty == true)
                          const _Badge('Web'),
                        if (widget.app.links['google']?.isNotEmpty == true)
                          const _Badge('Android'),
                        if (widget.app.links['ios']?.isNotEmpty == true)
                          const _Badge('iOS'),
                      ],
                    ),
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

/// ===============================
/// Platform Badge
/// ===============================
class _Badge extends StatelessWidget {
  final String label;
  const _Badge(this.label);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF2A2A2A)),
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: Color(0xFF10A37F),
          fontSize: 11,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}
