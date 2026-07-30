import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:go_router/go_router.dart';

import '../../../core/constants/api_constants.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/helpers.dart';
import '../widgets/admin_drawer.dart';

class AdminDashboardScreen extends ConsumerStatefulWidget {
  const AdminDashboardScreen({super.key});

  @override
  ConsumerState<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends ConsumerState<AdminDashboardScreen> {
  Map<String, dynamic>? _data;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetch();
  }

  Future<void> _fetch() async {
    setState(() => _loading = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      final res = await dio.get(ApiConstants.adminDashboard);
      setState(() { _data = res.data; _error = null; });
    } on DioException catch (e) {
      setState(() => _error = e.message ?? 'حدث خطأ في الاتصال');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('لوحة التحكم')),
      drawer: const AdminDrawer(currentRoute: '/admin'),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? _buildError()
              : RefreshIndicator(
                  onRefresh: _fetch,
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildStatsRow(),
                        const SizedBox(height: 24),
                        _buildSectionTitle('المستخدمون الجدد'),
                        const SizedBox(height: 12),
                        _buildRecentUsers(),
                        const SizedBox(height: 24),
                        _buildSectionTitle('أحدث البرومبتات'),
                        const SizedBox(height: 12),
                        _buildRecentPrompts(),
                        const SizedBox(height: 24),
                        _buildSectionTitle('إجراءات سريعة'),
                        const SizedBox(height: 12),
                        _buildQuickActions(),
                      ],
                    ),
                  ),
                ),
    );
  }

  Widget _buildError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off, size: 64, color: AppColors.error),
            const SizedBox(height: 16),
            Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: AppColors.error)),
            const SizedBox(height: 16),
            FilledButton.icon(onPressed: _fetch, icon: const Icon(Icons.refresh), label: const Text('إعادة المحاولة')),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsRow() {
    final stats = _data?['stats'] as Map<String, dynamic>? ?? {};
    return LayoutBuilder(
      builder: (_, constraints) => Wrap(
        spacing: 12,
        runSpacing: 12,
        children: [
          _statCard('إجمالي المستخدمين', '${stats['total_users'] ?? 0}', Icons.people_rounded, AppColors.primary, 1),
          if (constraints.maxWidth > 600) ...[
            _statCard('إجمالي البرومبتات', '${stats['total_prompts'] ?? 0}', Icons.auto_awesome_rounded, AppColors.secondary, 1),
          ],
        ].followedBy([
          _statCard('إجمالي البرومبتات', '${stats['total_prompts'] ?? 0}', Icons.auto_awesome_rounded, AppColors.secondary, 2),
          _statCard('عدد الزوار', '${stats['total_visitors'] ?? 0}', Icons.visibility_rounded, AppColors.tertiary, 2),
          _statCard('الإيرادات', '\$${(stats['revenue'] ?? 0).toStringAsFixed(0)}', Icons.trending_up_rounded, AppColors.gold, 2),
        ]).take(constraints.maxWidth > 600 ? 4 : 2).toList(),
      ),
    );
  }

  Widget _statCard(String label, String value, IconData icon, Color color, int flex) {
    return SizedBox(
      width: 160,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(color: color.withOpacity(0.12), borderRadius: BorderRadius.circular(10)),
                child: Icon(icon, color: color, size: 22),
              ),
              const SizedBox(height: 12),
              Text(value, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
              const SizedBox(height: 4),
              Text(label, style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(title, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold));
  }

  Widget _buildRecentUsers() {
    final users = (_data?['recent_users'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    if (users.isEmpty) return const Card(child: Padding(padding: EdgeInsets.all(24), child: Center(child: Text('لا يوجد مستخدمون جدد'))));
    return Card(
      child: Column(
        children: users.take(5).map((u) => ListTile(
          leading: CircleAvatar(
            radius: 18,
            backgroundColor: AppColors.primary.withOpacity(0.15),
            backgroundImage: u['profile_image'] != null ? NetworkImage(u['profile_image']) : null,
            child: u['profile_image'] == null ? const Icon(Icons.person, size: 18, color: AppColors.primary) : null,
          ),
          title: Text(u['username'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
          subtitle: Text(u['email'] ?? '', style: const TextStyle(fontSize: 12)),
          trailing: Text(_dateLabel(u['created_at']), style: TextStyle(color: Colors.grey.shade500, fontSize: 12)),
        )).toList(),
      ),
    );
  }

  Widget _buildRecentPrompts() {
    final prompts = (_data?['recent_prompts'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    if (prompts.isEmpty) return const Card(child: Padding(padding: EdgeInsets.all(24), child: Center(child: Text('لا يوجد برومبتات جديدة'))));
    return Card(
      child: Column(
        children: prompts.take(5).map((p) => ListTile(
          leading: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: AppColors.secondary.withOpacity(0.12), borderRadius: BorderRadius.circular(8)),
            child: const Icon(Icons.auto_awesome, size: 18, color: AppColors.secondary),
          ),
          title: Text(p['title'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14), maxLines: 1, overflow: TextOverflow.ellipsis),
          subtitle: Text('بواسطة ${p['author'] ?? 'مجهول'}', style: const TextStyle(fontSize: 12)),
          trailing: Text(_dateLabel(p['created_at']), style: TextStyle(color: Colors.grey.shade500, fontSize: 12)),
        )).toList(),
      ),
    );
  }

  Widget _buildQuickActions() {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        _actionChip(Icons.add, 'إضافة نموذج AI', () => context.go('/admin/models')),
        _actionChip(Icons.sync, 'مزامنة GitHub', () => _syncGithub()),
        _actionChip(Icons.eco, 'بذر البيانات', () => _seedData()),
      ],
    );
  }

  Widget _actionChip(IconData icon, String label, VoidCallback onTap) {
    return ActionChip(
      avatar: Icon(icon, size: 18, color: AppColors.primary),
      label: Text(label),
      onPressed: onTap,
    );
  }

  Future<void> _syncGithub() async {
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.post(ApiConstants.adminSyncGithub);
      if (mounted) Helpers.showToast('تمت المزامنة بنجاح');
      _fetch();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(Helpers.errorMessage(e), isError: true);
    }
  }

  Future<void> _seedData() async {
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.post(ApiConstants.adminSeedModels);
      await dio.post(ApiConstants.adminSeedCategories);
      if (mounted) Helpers.showToast('تم البذر بنجاح');
      _fetch();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(Helpers.errorMessage(e), isError: true);
    }
  }

  String _dateLabel(String? raw) {
    if (raw == null) return '';
    final dt = DateTime.tryParse(raw);
    if (dt == null) return '';
    return Helpers.timeAgo(dt);
  }
}
