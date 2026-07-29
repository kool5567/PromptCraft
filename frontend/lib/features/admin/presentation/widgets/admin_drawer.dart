import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_theme.dart';

class AdminDrawer extends StatelessWidget {
  final String currentRoute;

  const AdminDrawer({super.key, required this.currentRoute});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: const BoxDecoration(
              gradient: LinearGradient(colors: [AppColors.primary, AppColors.secondary]),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const CircleAvatar(
                  radius: 28,
                  backgroundColor: Colors.white,
                  child: Icon(Icons.admin_panel_settings, size: 28, color: AppColors.primary),
                ),
                const SizedBox(height: 10),
                Text('لوحة التحكم', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.white, fontWeight: FontWeight.bold)),
                Text('PromptCraft', style: TextStyle(color: Colors.white70, fontSize: 13)),
              ],
            ),
          ),
          _item(context, Icons.dashboard_rounded, 'الإحصائيات', '/admin', currentRoute == '/admin'),
          _item(context, Icons.people_rounded, 'المستخدمين', '/admin/users', currentRoute.startsWith('/admin/users')),
          _item(context, Icons.auto_awesome_rounded, 'البرومبتات', '/admin/prompts', currentRoute.startsWith('/admin/prompts')),
          _item(context, Icons.category_rounded, 'التصنيفات', '/admin/categories', currentRoute.startsWith('/admin/categories')),
          _item(context, Icons.memory_rounded, 'النماذج', '/admin/models', currentRoute.startsWith('/admin/models')),
          _item(context, Icons.download_rounded, 'الاستيراد', '/admin/imports', currentRoute.startsWith('/admin/imports')),
          _item(context, Icons.settings_rounded, 'الإعدادات', '/admin/settings', currentRoute.startsWith('/admin/settings')),
          _item(context, Icons.analytics_rounded, 'السجلات', '/admin/analytics', currentRoute.startsWith('/admin/analytics')),
          const Divider(height: 1),
          _item(context, Icons.home_rounded, 'العودة للموقع', '/', false),
        ],
      ),
    );
  }

  Widget _item(BuildContext context, IconData icon, String label, String route, bool active) {
    return Container(
      decoration: active ? BoxDecoration(
        color: AppColors.primary.withOpacity(0.08),
        border: const BorderDirectional(start: BorderSide(color: AppColors.primary, width: 3)),
      ) : null,
      child: ListTile(
        leading: Icon(icon, color: active ? AppColors.primary : null, size: 22),
        title: Text(label, style: TextStyle(
          fontWeight: active ? FontWeight.w600 : FontWeight.normal,
          color: active ? AppColors.primary : null,
        )),
        trailing: const Icon(Icons.chevron_left, size: 18),
        onTap: () {
          Navigator.pop(context);
          context.go(route);
        },
      ),
    );
  }
}
