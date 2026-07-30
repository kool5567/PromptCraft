import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';

import '../../../core/constants/api_constants.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/helpers.dart';
import '../widgets/admin_drawer.dart';

class AdminUsersScreen extends ConsumerStatefulWidget {
  const AdminUsersScreen({super.key});

  @override
  ConsumerState<AdminUsersScreen> createState() => _AdminUsersScreenState();
}

class _AdminUsersScreenState extends ConsumerState<AdminUsersScreen> {
  final _searchCtrl = TextEditingController();
  String _filter = 'الكل';
  List<Map<String, dynamic>> _users = [];
  bool _loading = true;
  int _page = 1;
  int _totalPages = 1;

  @override
  void initState() {
    super.initState();
    _fetch();
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  Future<void> _fetch() async {
    setState(() => _loading = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      final params = <String, dynamic>{'page': _page, 'per_page': 20};
      if (_searchCtrl.text.trim().isNotEmpty) params['search'] = _searchCtrl.text.trim();
      final roleMap = {'المشرفين': 'admin', 'المستخدمين': 'user', 'المميزين': 'premium'};
      if (roleMap.containsKey(_filter)) params['role'] = roleMap[_filter];
      final res = await dio.get(ApiConstants.adminUsers, queryParameters: params);
      setState(() {
        _users = (res.data['users'] as List?)?.cast<Map<String, dynamic>>() ?? [];
        _totalPages = (res.data['total_pages'] ?? 1) as int;
      });
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _updateRole(String userId, String role) async {
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.put(ApiConstants.adminUser(userId), data: {'role': role});
      if (mounted) Helpers.showToast('تم تحديث الصلاحية');
      _fetch();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    }
  }

  Future<void> _toggleBan(String userId, bool currentlyActive) async {
    final confirmed = await Helpers.showConfirmDialog(
      context, currentlyActive ? 'حظر المستخدم' : 'تفعيل المستخدم',
      currentlyActive ? 'هل أنت متأكد من حظر هذا المستخدم؟' : 'هل أنت متأكد من إعادة تفعيل هذا المستخدم؟',
    );
    if (!confirmed) return;
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.put(ApiConstants.adminUser(userId), data: {'is_active': !currentlyActive});
      if (mounted) Helpers.showToast(currentlyActive ? 'تم الحظر' : 'تم التفعيل');
      _fetch();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    }
  }

  Future<void> _deleteUser(String userId) async {
    final confirmed = await Helpers.showConfirmDialog(context, 'حذف المستخدم', 'هل أنت متأكد من حذف هذا المستخدم؟ لا يمكن التراجع عن هذا الإجراء.');
    if (!confirmed) return;
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.delete(ApiConstants.adminUser(userId));
      if (mounted) Helpers.showToast('تم الحذف');
      _fetch();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('المستخدمين')),
      drawer: const AdminDrawer(currentRoute: '/admin/users'),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: TextField(
              controller: _searchCtrl,
              decoration: InputDecoration(
                hintText: 'بحث عن مستخدم...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchCtrl.text.isNotEmpty
                    ? IconButton(icon: const Icon(Icons.clear), onPressed: () { _searchCtrl.clear(); _fetch(); })
                    : null,
              ),
              onSubmitted: (_) => _fetch(),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: ['الكل', 'المشرفين', 'المستخدمين', 'المميزين'].map((f) {
                  final sel = _filter == f;
                  return Padding(
                    padding: const EdgeInsets.only(left: 8),
                    child: FilterChip(
                      label: Text(f, style: TextStyle(fontSize: 13, color: sel ? Colors.white : null)),
                      selected: sel,
                      selectedColor: AppColors.primary,
                      onSelected: (_) { setState(() => _filter = f); _fetch(); },
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _users.isEmpty
                    ? const Center(child: Text('لا يوجد مستخدمين'))
                    : Column(
                        children: [
                          Expanded(
                            child: RefreshIndicator(
                              onRefresh: _fetch,
                              child: ListView.builder(
                                padding: const EdgeInsets.symmetric(horizontal: 16),
                                itemCount: _users.length,
                                itemBuilder: (_, i) {
                                  final u = _users[i];
                                  final role = u['role'] ?? 'user';
                                  final active = u['is_active'] ?? true;
                                  return Card(
                                    margin: const EdgeInsets.only(bottom: 8),
                                    child: ListTile(
                                      leading: CircleAvatar(
                                        radius: 20,
                                        backgroundColor: AppColors.primary.withOpacity(0.15),
                                        backgroundImage: u['profile_image'] != null ? NetworkImage(u['profile_image']) : null,
                                        child: u['profile_image'] == null
                                            ? Text((u['username'] ?? '?')[0].toUpperCase(), style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold))
                                            : null,
                                      ),
                                      title: Text(u['username'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                                      subtitle: Text(u['email'] ?? '', style: const TextStyle(fontSize: 12)),
                                      trailing: Row(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          _roleBadge(role),
                                          const SizedBox(width: 6),
                                          Container(
                                            width: 8, height: 8,
                                            decoration: BoxDecoration(shape: BoxShape.circle, color: active ? AppColors.secondary : AppColors.error),
                                          ),
                                          const SizedBox(width: 8),
                                          PopupMenuButton<String>(
                                            icon: const Icon(Icons.more_vert, size: 20),
                                            onSelected: (v) {
                                              switch (v) {
                                                case 'role': _showRoleDialog(u['id'], role); break;
                                                case 'ban': _toggleBan(u['id'], active); break;
                                                case 'delete': _deleteUser(u['id']); break;
                                              }
                                            },
                                            itemBuilder: (_) => [
                                              const PopupMenuItem(value: 'role', child: ListTile(leading: Icon(Icons.shield, size: 20), title: Text('تعديل الصلاحية'))),
                                              PopupMenuItem(
                                                value: 'ban',
                                                child: ListTile(
                                                  leading: Icon(active ? Icons.block : Icons.check_circle, size: 20, color: active ? AppColors.error : AppColors.secondary),
                                                  title: Text(active ? 'حظر' : 'تفعيل'),
                                                ),
                                              ),
                                              const PopupMenuItem(
                                                value: 'delete',
                                                child: ListTile(leading: Icon(Icons.delete, size: 20, color: AppColors.error), title: Text('حذف', style: TextStyle(color: AppColors.error))),
                                              ),
                                            ],
                                          ),
                                        ],
                                      ),
                                    ),
                                  );
                                },
                              ),
                            ),
                          ),
                          if (_totalPages > 1)
                            Padding(
                              padding: const EdgeInsets.all(16),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  IconButton(
                                    icon: const Icon(Icons.chevron_right),
                                    onPressed: _page > 1 ? () { setState(() => _page--); _fetch(); } : null,
                                  ),
                                  Text('$_page / $_totalPages'),
                                  IconButton(
                                    icon: const Icon(Icons.chevron_left),
                                    onPressed: _page < _totalPages ? () { setState(() => _page++); _fetch(); } : null,
                                  ),
                                ],
                              ),
                            ),
                        ],
                      ),
          ),
        ],
      ),
    );
  }

  Widget _roleBadge(String role) {
    Color color;
    String label;
    switch (role) {
      case 'admin': case 'superadmin': color = AppColors.error; label = 'مشرف'; break;
      case 'premium': color = AppColors.gold; label = 'مميز'; break;
      default: color = Colors.grey; label = 'مستخدم';
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(color: color.withOpacity(0.12), borderRadius: BorderRadius.circular(6)),
      child: Text(label, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w500)),
    );
  }

  void _showRoleDialog(String userId, String currentRole) {
    final roles = ['user', 'premium', 'admin'];
    String selected = currentRole;
    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (_, setDialogState) => AlertDialog(
          title: const Text('تعديل الصلاحية'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: roles.map((r) {
              final labels = {'user': 'مستخدم', 'premium': 'مميز', 'admin': 'مشرف'};
              return RadioListTile<String>(
                title: Text(labels[r] ?? r),
                value: r,
                groupValue: selected,
                onChanged: (v) { if (v != null) setDialogState(() => selected = v); },
              );
            }).toList(),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('إلغاء')),
            FilledButton(onPressed: () { Navigator.pop(ctx); _updateRole(userId, selected); }, child: const Text('حفظ')),
          ],
        ),
      ),
    );
  }
}
