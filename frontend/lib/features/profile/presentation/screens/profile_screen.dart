import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/network/dio_client.dart';
import '../../../data/repositories/auth_repository.dart';
import '../../../domain/entities/user_model.dart';

final _currentUserProvider = FutureProvider.autoDispose<UserModel?>((ref) {
  return ref.read(authRepositoryProvider).getProfile();
});

final _profileStatsProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final dio = ref.read(dioClientProvider).dio;
  final response = await dio.get(ApiConstants.userStats);
  final data = response.data;
  if (data is Map) return data as Map<String, dynamic>;
  if (data is Map && data['data'] is Map) return data['data'] as Map<String, dynamic>;
  return {};
});

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAsync = ref.watch(_currentUserProvider);
    final statsAsync = ref.watch(_profileStatsProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: userAsync.when(
        data: (user) => _ProfileBody(user: user, statsAsync: statsAsync),
        loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
        error: (err, _) => Scaffold(
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.error_outline, size: 64, color: Theme.of(context).colorScheme.error),
                const SizedBox(height: 16),
                Text('حدث خطأ في تحميل الملف الشخصي', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                TextButton(
                  onPressed: () => ref.invalidate(_currentUserProvider),
                  child: const Text('إعادة المحاولة'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ProfileBody extends ConsumerWidget {
  final UserModel? user;
  final AsyncValue<Map<String, dynamic>> statsAsync;

  const _ProfileBody({required this.user, required this.statsAsync});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final stats = statsAsync.asData?.value ?? {};

    return Scaffold(
      appBar: AppBar(
        title: const Text('الملف الشخصي'),
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            _ProfileHeader(user: user, colorScheme: colorScheme, theme: theme),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
              child: Row(
                children: [
                  _StatCard(
                    icon: Icons.auto_awesome,
                    label: 'النصوص',
                    value: '${stats['total_prompts'] ?? stats['totalPrompts'] ?? '-'}',
                    color: colorScheme.primary,
                  ),
                  const SizedBox(width: 12),
                  _StatCard(
                    icon: Icons.folder_outlined,
                    label: 'المجموعات',
                    value: '${stats['total_collections'] ?? stats['totalCollections'] ?? '-'}',
                    color: colorScheme.tertiary,
                  ),
                  const SizedBox(width: 12),
                  _StatCard(
                    icon: Icons.favorite_outlined,
                    label: 'المفضلة',
                    value: '${stats['total_favorites'] ?? stats['totalFavorites'] ?? '-'}',
                    color: Colors.redAccent,
                  ),
                ],
              ),
            ),
            if (user != null) ...[
              const SizedBox(height: 16),
              _SubscriptionCard(user: user!, colorScheme: colorScheme, theme: theme),
            ],
            const SizedBox(height: 16),
            _MenuSection(
              items: [
                _MenuItemData(
                  icon: Icons.library_books_outlined,
                  title: 'المكتبة الشخصية',
                  onTap: () => context.push('/library'),
                ),
                _MenuItemData(
                  icon: Icons.folder_outlined,
                  title: 'المجموعات',
                  onTap: () => context.push('/collections'),
                ),
                _MenuItemData(
                  icon: Icons.favorite_outlined,
                  title: 'المفضلة',
                  onTap: () => context.push('/favorites'),
                ),
                _MenuItemData(
                  icon: Icons.auto_fix_high_outlined,
                  title: 'القوالب',
                  onTap: () => context.push('/templates'),
                ),
                _MenuItemData(
                  icon: Icons.settings_outlined,
                  title: 'الإعدادات',
                  onTap: () => context.push('/settings'),
                ),
                _MenuItemData(
                  icon: Icons.help_outline,
                  title: 'المساعدة والدعم',
                  onTap: () {
                    // Navigate to help
                  },
                ),
              ],
            ),
            if (user?.isAdmin == true) ...[
              const SizedBox(height: 4),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Card(
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                    side: BorderSide(color: colorScheme.outlineVariant),
                  ),
                  child: ListTile(
                    leading: Icon(Icons.dashboard_outlined, color: colorScheme.error),
                    title: const Text('لوحة التحكم'),
                    trailing: Icon(Icons.chevron_left, color: colorScheme.onSurfaceVariant, size: 20),
                    onTap: () => context.push('/admin'),
                  ),
                ),
              ),
            ],
            const SizedBox(height: 4),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
              child: OutlinedButton.icon(
                onPressed: () => _showLogoutDialog(context, ref),
                style: OutlinedButton.styleFrom(
                  foregroundColor: colorScheme.error,
                  side: BorderSide(color: colorScheme.error.withOpacity(0.5)),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                ),
                icon: const Icon(Icons.logout_rounded),
                label: const Text('تسجيل الخروج', style: TextStyle(fontSize: 15)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showLogoutDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('تسجيل الخروج'),
        content: const Text('هل أنت متأكد من رغبتك في تسجيل الخروج؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('إلغاء'),
          ),
          FilledButton(
            onPressed: () async {
              Navigator.pop(ctx);
              try {
                await ref.read(authRepositoryProvider).logout();
                if (context.mounted) context.go('/login');
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: const Text('حدث خطأ أثناء تسجيل الخروج'),
                      behavior: SnackBarBehavior.floating,
                    ),
                  );
                }
              }
            },
            style: FilledButton.styleFrom(backgroundColor: Theme.of(context).colorScheme.error),
            child: const Text('تسجيل الخروج'),
          ),
        ],
      ),
    );
  }
}

class _ProfileHeader extends StatelessWidget {
  final UserModel? user;
  final ColorScheme colorScheme;
  final ThemeData theme;

  const _ProfileHeader({
    required this.user,
    required this.colorScheme,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [colorScheme.primaryContainer, colorScheme.surface],
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
        ),
      ),
      child: Column(
        children: [
          _buildAvatar(),
          const SizedBox(height: 12),
          Text(
            user?.displayName ?? user?.username ?? '',
            style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(
            user?.email ?? '',
            style: theme.textTheme.bodyMedium?.copyWith(color: colorScheme.onSurfaceVariant),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: (user?.isActive == true ? Colors.green : Colors.grey).withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              user?.isActive == true ? 'نشط' : 'غير نشط',
              style: TextStyle(
                color: user?.isActive == true ? Colors.green : Colors.grey,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAvatar() {
    final name = user?.displayName ?? user?.username ?? '';
    final initials = name.isNotEmpty
        ? name.split(' ').take(2).map((e) => e.isNotEmpty ? e[0].toUpperCase() : '').join()
        : '?';
    final hasImage = user?.profileImage != null && user!.profileImage!.isNotEmpty;

    return Container(
      width: 96,
      height: 96,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: colorScheme.primary,
        boxShadow: [
          BoxShadow(
            color: colorScheme.primary.withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: hasImage
          ? Image.network(
              user!.profileImage!,
              fit: BoxFit.cover,
              width: 96,
              height: 96,
              errorBuilder: (_, __, ___) => _buildInitialsText(initials),
              loadingBuilder: (_, child, progress) {
                if (progress == null) return child;
                return const Center(
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                );
              },
            )
          : _buildInitialsText(initials),
    );
  }

  Widget _buildInitialsText(String initials) {
    return Center(
      child: Text(
        initials.isNotEmpty ? initials : '?',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 28,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _StatCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Expanded(
      child: Card(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: theme.colorScheme.outlineVariant),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
          child: Column(
            children: [
              Icon(icon, color: color, size: 28),
              const SizedBox(height: 8),
              Text(
                value,
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                label,
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SubscriptionCard extends StatelessWidget {
  final UserModel user;
  final ColorScheme colorScheme;
  final ThemeData theme;

  const _SubscriptionCard({
    required this.user,
    required this.colorScheme,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Card(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: colorScheme.outlineVariant),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: colorScheme.primaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  user.isPremium ? Icons.star_rounded : Icons.person_outlined,
                  color: colorScheme.primary,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'الباقة الحالية',
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      _subscriptionLabel(user.subscriptionTier),
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              if (!user.isPremium)
                FilledButton.tonalIcon(
                  onPressed: () => context.push('/subscription'),
                  icon: const Icon(Icons.arrow_upward, size: 18),
                  label: const Text('ترقية'),
                ),
            ],
          ),
        ),
      ),
    );
  }

  String _subscriptionLabel(String tier) {
    switch (tier) {
      case 'free':
        return 'مجاني';
      case 'basic':
        return 'أساسي';
      case 'premium':
        return 'ممتاز';
      case 'pro':
        return 'احترافي';
      default:
        return tier;
    }
  }
}

class _MenuItemData {
  final IconData icon;
  final String title;
  final VoidCallback onTap;

  const _MenuItemData({
    required this.icon,
    required this.title,
    required this.onTap,
  });
}

class _MenuSection extends StatelessWidget {
  final List<_MenuItemData> items;

  const _MenuSection({required this.items});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Card(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: colorScheme.outlineVariant),
        ),
        child: ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: items.length,
          separatorBuilder: (_, __) => Divider(
            height: 1,
            indent: 56,
            color: colorScheme.outlineVariant.withOpacity(0.5),
          ),
          itemBuilder: (context, index) {
            final item = items[index];
            return ListTile(
              leading: Icon(item.icon, color: colorScheme.onSurfaceVariant),
              title: Text(item.title),
              trailing: Icon(
                Icons.chevron_left,
                color: colorScheme.onSurfaceVariant,
                size: 20,
              ),
              onTap: item.onTap,
            );
          },
        ),
      ),
    );
  }
}
