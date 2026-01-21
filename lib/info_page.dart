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
        padding: const EdgeInsets.all(16),
        children: const [
          _SectionHeader(title: 'SEADICE'),
          _InfoCard(
            title: 'About',
            description:
                'Small, useful, fun apps.\n'
                'SEADICE is a personal app studio that builds '
                'simple games, utilities, and learning tools.',
          ),

          SizedBox(height: 16),

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

          SizedBox(height: 16),

          _SectionHeader(title: 'Contact'),
          _LinkCard(
            title: 'Email',
            subtitle: 'お問い合わせはこちら',
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
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 18,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

/// ===============================
/// Info Card (text only)
/// ===============================
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
          const SizedBox(height: 8),
          Text(
            description,
            style: const TextStyle(
              color: Color(0xFFB0B0B0),
              fontSize: 13,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}

/// ===============================
/// Link Card
/// ===============================
class _LinkCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final String url;
  const _LinkCard({
    required this.title,
    required this.subtitle,
    required this.url,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(12),
      onTap: () => _launch(url),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF1E1E1E),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFF2A2A2A)),
        ),
        child: Row(
          children: [
            Expanded(
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
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      color: Color(0xFFB0B0B0),
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(Icons.open_in_new, size: 16, color: Color(0xFF808080)),
          ],
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
          style: TextStyle(color: Color(0xFF808080), fontSize: 12),
        ),
      ],
    );
  }
}
