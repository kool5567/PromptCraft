import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/theme/app_theme.dart';
import 'core/storage/secure_storage.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: PromptCraftApp()));
}

class PromptCraftApp extends ConsumerStatefulWidget {
  const PromptCraftApp({super.key});

  @override
  ConsumerState<PromptCraftApp> createState() => _PromptCraftAppState();
}

class _PromptCraftAppState extends ConsumerState<PromptCraftApp> {
  ThemeMode _themeMode = ThemeMode.system;

  @override
  void initState() {
    super.initState();
    _loadTheme();
  }

  Future<void> _loadTheme() async {
    final storage = ref.read(secureStorageProvider);
    final saved = await storage.getThemeMode();
    if (mounted) {
      setState(() {
        switch (saved) {
          case 'light': _themeMode = ThemeMode.light; break;
          case 'dark': _themeMode = ThemeMode.dark; break;
          default: _themeMode = ThemeMode.system;
        }
      });
    }
  }

  void _setThemeMode(ThemeMode mode) {
    setState(() => _themeMode = mode);
    ref.read(secureStorageProvider).saveThemeMode(mode.name);
  }

  @override
  Widget build(BuildContext context) {
    final router = ref.watch(routerProvider);
    return MaterialApp.router(
      title: 'PromptCraft',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: _themeMode,
      routerConfig: router,
      locale: const Locale('ar'),
      supportedLocales: const [Locale('ar'), Locale('en')],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
    );
  }
}
