import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  ThemeMode _themeMode = ThemeMode.system;
  String _language = 'ar';
  bool _pushNotifications = true;
  bool _emailNotifications = true;
  bool _soundEnabled = true;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('الإعدادات'),
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'المظهر',
                style: theme.textTheme.titleSmall?.copyWith(
                  color: colorScheme.primary,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Card(
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                  side: BorderSide(color: colorScheme.outlineVariant),
                ),
                child: Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.brightness_6_outlined, color: colorScheme.onSurfaceVariant),
                              const SizedBox(width: 12),
                              Text('السمة', style: theme.textTheme.bodyLarge),
                              const Spacer(),
                              Text(
                                _themeMode == ThemeMode.light
                                    ? 'فاتح'
                                    : _themeMode == ThemeMode.dark
                                        ? 'داكن'
                                        : 'النظام',
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  color: colorScheme.onSurfaceVariant,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          SegmentedButton<ThemeMode>(
                            segments: const [
                              ButtonSegment(
                                value: ThemeMode.light,
                                label: Text('فاتح'),
                                icon: Icon(Icons.light_mode_outlined, size: 18),
                              ),
                              ButtonSegment(
                                value: ThemeMode.dark,
                                label: Text('داكن'),
                                icon: Icon(Icons.dark_mode_outlined, size: 18),
                              ),
                              ButtonSegment(
                                value: ThemeMode.system,
                                label: Text('النظام'),
                                icon: Icon(Icons.settings_brightness_outlined, size: 18),
                              ),
                            ],
                            selected: {_themeMode},
                            onSelectionChanged: (selected) {
                              setState(() => _themeMode = selected.first);
                            },
                            style: ButtonStyle(
                              visualDensity: VisualDensity.compact,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Divider(height: 1, indent: 16, color: colorScheme.outlineVariant.withOpacity(0.5)),
                    ListTile(
                      leading: Icon(Icons.language_outlined, color: colorScheme.onSurfaceVariant),
                      title: const Text('اللغة'),
                      trailing: DropdownButton<String>(
                        value: _language,
                        underline: const SizedBox(),
                        style: theme.textTheme.bodyMedium,
                        items: const [
                          DropdownMenuItem(value: 'ar', child: Text('العربية')),
                          DropdownMenuItem(value: 'en', child: Text('English')),
                        ],
                        onChanged: (value) {
                          if (value != null) setState(() => _language = value);
                        },
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'الإشعارات',
                style: theme.textTheme.titleSmall?.copyWith(
                  color: colorScheme.primary,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Card(
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                  side: BorderSide(color: colorScheme.outlineVariant),
                ),
                child: Column(
                  children: [
                    SwitchListTile(
                      secondary: Icon(Icons.push_pin_outlined, color: colorScheme.onSurfaceVariant),
                      title: const Text('إشعارات التطبيق'),
                      value: _pushNotifications,
                      onChanged: (v) => setState(() => _pushNotifications = v),
                    ),
                    Divider(height: 1, indent: 56, color: colorScheme.outlineVariant.withOpacity(0.5)),
                    SwitchListTile(
                      secondary: Icon(Icons.email_outlined, color: colorScheme.onSurfaceVariant),
                      title: const Text('الإشعارات البريدية'),
                      value: _emailNotifications,
                      onChanged: (v) => setState(() => _emailNotifications = v),
                    ),
                    Divider(height: 1, indent: 56, color: colorScheme.outlineVariant.withOpacity(0.5)),
                    SwitchListTile(
                      secondary: Icon(Icons.volume_up_outlined, color: colorScheme.onSurfaceVariant),
                      title: const Text('الصوت'),
                      value: _soundEnabled,
                      onChanged: (v) => setState(() => _soundEnabled = v),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'الذاكرة المؤقتة',
                style: theme.textTheme.titleSmall?.copyWith(
                  color: colorScheme.primary,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Card(
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                  side: BorderSide(color: colorScheme.outlineVariant),
                ),
                child: ListTile(
                  leading: Icon(Icons.cleaning_services_outlined, color: colorScheme.onSurfaceVariant),
                  title: const Text('مسح الذاكرة المؤقتة'),
                  subtitle: const Text('حذف البيانات المخزنة مؤقتاً'),
                  trailing: Icon(Icons.chevron_left, color: colorScheme.onSurfaceVariant, size: 20),
                  onTap: () => _showCacheClearDialog(context),
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'حول',
                style: theme.textTheme.titleSmall?.copyWith(
                  color: colorScheme.primary,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Card(
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                  side: BorderSide(color: colorScheme.outlineVariant),
                ),
                child: Column(
                  children: [
                    ListTile(
                      leading: Icon(Icons.info_outlined, color: colorScheme.onSurfaceVariant),
                      title: const Text('الإصدار'),
                      trailing: const Text('1.0.0'),
                    ),
                    Divider(height: 1, indent: 56, color: colorScheme.outlineVariant.withOpacity(0.5)),
                    ListTile(
                      leading: Icon(Icons.description_outlined, color: colorScheme.onSurfaceVariant),
                      title: const Text('التراخيص'),
                      trailing: Icon(Icons.chevron_left, color: colorScheme.onSurfaceVariant, size: 20),
                      onTap: () {
                        showLicensePage(
                          context: context,
                          applicationName: 'PromptCraft',
                          applicationVersion: '1.0.0',
                        );
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  void _showCacheClearDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('مسح الذاكرة المؤقتة'),
        content: const Text('سيتم حذف جميع البيانات المخزنة مؤقتاً. هل أنت متأكد؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: const Text('تم مسح الذاكرة المؤقتة بنجاح'),
                  behavior: SnackBarBehavior.floating,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              );
            },
            child: const Text('مسح'),
          ),
        ],
      ),
    );
  }
}
