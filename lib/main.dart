import 'package:flutter/material.dart';
import 'home_page.dart'; // Hero（Welcome）
import 'apps_page.dart'; // アプリ一覧（今作ってるGrid）
import 'info_page.dart'; // About / Legal

void main() async {
  runApp(const SeadiceApp());
}

/// ===============================
/// App Root
/// ===============================
class SeadiceApp extends StatelessWidget {
  const SeadiceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'SEADICE',
      theme: _seadiceTheme,
      home: const RootPage(),
    );
  }
}

/// ===============================
/// Theme (ChatGPT Style)
/// ===============================
final ThemeData _seadiceTheme = ThemeData(
  brightness: Brightness.dark,
  scaffoldBackgroundColor: const Color(0xFF0F0F0F),
  primaryColor: const Color(0xFF10A37F),

  appBarTheme: const AppBarTheme(
    backgroundColor: Color(0xFF0F0F0F),
    elevation: 0,
    centerTitle: false,
    titleTextStyle: TextStyle(
      color: Colors.white,
      fontSize: 18,
      fontWeight: FontWeight.w600,
    ),
  ),

  textTheme: const TextTheme(
    bodyLarge: TextStyle(color: Colors.white),
    bodyMedium: TextStyle(color: Color(0xFFB0B0B0)),
  ),

  bottomNavigationBarTheme: const BottomNavigationBarThemeData(
    backgroundColor: Color(0xFF0F0F0F),
    selectedItemColor: Color(0xFF10A37F),
    unselectedItemColor: Color(0xFF808080),
    type: BottomNavigationBarType.fixed,
    elevation: 0,
  ),
);

/// ===============================
/// Root Page with BottomNavigation
/// ===============================
class RootPage extends StatefulWidget {
  const RootPage({super.key});

  @override
  State<RootPage> createState() => _RootPageState();
}

class _RootPageState extends State<RootPage> {
  int _index = 0;

  final List<Widget> _pages = const [
    HomePage(), // Hero
    AppsPage(), // App List
    InfoPage(), // Info / Legal
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _index, children: _pages),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _index,
        onTap: (i) => setState(() => _index = i),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.apps_outlined),
            activeIcon: Icon(Icons.apps),
            label: 'Apps',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.info_outline),
            activeIcon: Icon(Icons.info),
            label: 'Info',
          ),
        ],
      ),
    );
  }
}
