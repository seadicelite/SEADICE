import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class InfoPage extends StatelessWidget {
  const InfoPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0F0F),
      appBar: AppBar(
        title: const Text('Info'),
        backgroundColor: const Color(0xFF0F0F0F),
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
        children: const [
          _SectionHeader(title: 'SEADICE'),

          _InfoCard(
            title: 'About',
            description:
                'SEADICE is an independent app studio creating '
                'small, useful, and fun apps.\n\n'
                'We build games, utilities, and learning tools '
                'designed for everyday moments.',
          ),

          SizedBox(height: 24),

          _SectionHeader(title: 'Legal'),

          _LinkCard(
            title: 'Privacy Policy',
            subtitle: '個人情報の取り扱いについて',
            url: 'https://seadice.app/legal/privacy',
          ),
          _LinkCard(
            title: 'Terms of Service',
            subtitle: '利用規約',
            url: 'https://seadice.app/legal/terms',
          ),

          SizedBox(height: 24),

          _SectionHeader(title: 'Contact'),

          _LinkCard(
            title: 'Email',
            subtitle: 'contact@seadice.app',
            url: 'mailto:contact@seadice.app',
          ),

          SizedBox(height: 32),

          _FooterNote(),
        ],
      ),
    );
  }
}

/// ===============================
/// Section Header
/// ===============================
class _SectionHeader extends StatelessWidget {
  final String title;
  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Text(
        title,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 18,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.3,
        ),
      ),
    );
  }
}

/// ===============================
/// Info Card（読む用）
// ===============================
class _InfoCard extends StatelessWidget {
  final String title;
  final String description;
  const _InfoCard({required this.title, required this.description});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E1E),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF2A2A2A)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            description,
            style: const TextStyle(
              color: Color(0xFFB0B0B0),
              fontSize: 13,
              height: 1.55,
            ),
          ),
        ],
      ),
    );
  }
}

/// ===============================
/// Link Card（Hover対応）
/// ===============================
class _LinkCard extends StatefulWidget {
  final String title;
  final String subtitle;
  final String url;

  const _LinkCard({
    required this.title,
    required this.subtitle,
    required this.url,
  });

  @override
  State<_LinkCard> createState() => _LinkCardState();
}

class _LinkCardState extends State<_LinkCard> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final isPc = MediaQuery.of(context).size.width >= 900;

    return MouseRegion(
      onEnter: (_) => isPc ? setState(() => _hover = true) : null,
      onExit: (_) => isPc ? setState(() => _hover = false) : null,
      child: GestureDetector(
        onTap: () => _launch(widget.url),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF1E1E1E),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: _hover ? const Color(0xFF10A37F) : const Color(0xFF2A2A2A),
            ),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.title,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.subtitle,
                      style: const TextStyle(
                        color: Color(0xFFB0B0B0),
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.open_in_new,
                size: 16,
                color: _hover
                    ? const Color(0xFF10A37F)
                    : const Color(0xFF808080),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _launch(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }
}

/// ===============================
/// Footer
/// ===============================
class _FooterNote extends StatelessWidget {
  const _FooterNote();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: const [
        Divider(color: Color(0xFF2A2A2A)),
        SizedBox(height: 12),
        Text(
          '© 2026 SEADICE',
          style: TextStyle(
            color: Color(0xFF808080),
            fontSize: 12,
            letterSpacing: 0.2,
          ),
        ),
      ],
    );
  }
}
