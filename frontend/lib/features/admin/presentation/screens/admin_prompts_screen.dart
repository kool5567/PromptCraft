import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/api_constants.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/utils/helpers.dart';
import '../widgets/admin_drawer.dart';

class AdminPromptsScreen extends ConsumerStatefulWidget {
  const AdminPromptsScreen({super.key});

  @override
  ConsumerState<AdminPromptsScreen> createState() => _AdminPromptsScreenState();
}

class _AdminPromptsScreenState extends ConsumerState<AdminPromptsScreen> {
  final _searchCtrl = TextEditingController();
  String _filter = 'all';
  List<Map<String, dynamic>> _prompts = [];
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
      if (_filter != 'all') params['status'] = _filter;
      final res = await dio.get(ApiConstants.adminPrompts, queryParameters: params);
      setState(() {
        _prompts = (res.data['prompts'] as List?)?.cast<Map<String, dynamic>>() ?? [];
        _totalPages = (res.data['total_pages'] ?? 1) as int;
      });
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _changeStatus(String id, String status) async {
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.put(ApiConstants.adminPromptStatus(id), data: {'status': status});
      if (mounted) Helpers.showToast('تم تغيير الحالة');
      _fetch();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    }
  }

  Future<void> _toggleFeature(String id, bool featured) async {
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.put(ApiConstants.adminPromptStatus(id), data: {'is_featured': !featured});
      if (mounted) Helpers.showToast(featured ? 'إزالة التمييز' : 'تم التمييز');
      _fetch();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    }
  }

  Future<void> _deletePrompt(String id) async {
    final confirmed = await Helpers.showConfirmDialog(context, 'حذف البرومبت', 'هل أنت متأكد من حذف هذا البرومبت؟');
    if (!confirmed) return;
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.delete('${ApiConstants.adminPrompts}/$id');
      if (mounted) Helpers.showToast('تم الحذف');
      _fetch();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('البرومبتات'),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _fetch)],
      ),
      drawer: const AdminDrawer(currentRoute: '/admin/prompts'),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: TextField(
              controller: _searchCtrl,
              decoration: InputDecoration(
                hintText: 'بحث عن برومبت...',
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
                children: [
                  _filterChip('الكل', _filter == 'all', () => setState(() { _filter = 'all'; _fetch(); })),
                  const SizedBox(width: 8),
                  _filterChip('منشور', _filter == 'published', () => setState(() { _filter = 'published'; _fetch(); })),
                  const SizedBox(width: 8),
                  _filterChip('مسودة', _filter == 'draft', () => setState(() { _filter = 'draft'; _fetch(); })),
                  const SizedBox(width: 8),
                  _filterChip('مؤرشف', _filter == 'archived', () => setState(() { _filter = 'archived'; _fetch(); })),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _prompts.isEmpty
                    ? const Center(child: Text('لا يوجد برومبتات'))
                    : RefreshIndicator(
                        onRefresh: _fetch,
                        child: ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: _prompts.length,
                          itemBuilder: (_, i) {
                            final p = _prompts[i];
                            final status = p['status'] ?? 'published';
                            return Card(
                              margin: const EdgeInsets.only(bottom: 8),
                              child: ListTile(
                                leading: Container(
                                  padding: const EdgeInsets.all(8),
                                  decoration: BoxDecoration(
                                    color: p['is_featured'] == true ? AppColors.gold.withOpacity(0.15) : AppColors.primary.withOpacity(0.1),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Icon(
                                    p['is_featured'] == true ? Icons.star : Icons.auto_awesome,
                                    size: 20,
                                    color: p['is_featured'] == true ? AppColors.gold : AppColors.primary,
                                  ),
                                ),
                                title: Text(p['title'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14), maxLines: 1, overflow: TextOverflow.ellipsis),
                                subtitle: Text('بواسطة ${p['author'] ?? 'مجهول'} • ${_dateLabel(p['created_at'])}', style: const TextStyle(fontSize: 12)),
                                trailing: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    _statusBadge(status),
                                    const SizedBox(width: 4),
                                    PopupMenuButton<String>(
                                      icon: const Icon(Icons.more_vert, size: 20),
                                      onSelected: (v) {
                                        switch (v) {
                                          case 'view': context.go('/prompts/${p['id']}'); break;
                                          case 'publish': _changeStatus(p['id'], 'published'); break;
                                          case 'draft': _changeStatus(p['id'], 'draft'); break;
                                          case 'archive': _changeStatus(p['id'], 'archived'); break;
                                          case 'feature': _toggleFeature(p['id'], p['is_featured'] == true); break;
                                          case 'delete': _deletePrompt(p['id']); break;
                                        }
                                      },
                                      itemBuilder: (_) => [
                                        const PopupMenuItem(value: 'view', child: ListTile(leading: Icon(Icons.visibility, size: 20), title: Text('عرض'))),
                                        if (status != 'published')
                                          const PopupMenuItem(value: 'publish', child: ListTile(leading: Icon(Icons.check_circle, size: 20, color: AppColors.secondary), title: Text('نشر'))),
                                        if (status != 'draft')
                                          const PopupMenuItem(value: 'draft', child: ListTile(leading: Icon(Icons.edit_note, size: 20), title: Text('مسودة'))),
                                        if (status != 'archived')
                                          const PopupMenuItem(value: 'archive', child: ListTile(leading: Icon(Icons.archive, size: 20), title: Text('أرشفة'))),
                                        PopupMenuItem(
                                          value: 'feature',
                                          child: ListTile(
                                            leading: Icon(p['is_featured'] == true ? Icons.star_border : Icons.star, size: 20, color: AppColors.gold),
                                            title: Text(p['is_featured'] == true ? 'إزالة التمييز' : 'تمييز'),
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
              padding: const EdgeInsets.all(12),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  IconButton(icon: const Icon(Icons.chevron_right), onPressed: _page > 1 ? () { setState(() => _page--); _fetch(); } : null),
                  Text('$_page / $_totalPages', style: const TextStyle(fontSize: 13)),
                  IconButton(icon: const Icon(Icons.chevron_left), onPressed: _page < _totalPages ? () { setState(() => _page++); _fetch(); } : null),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _filterChip(String label, bool selected, VoidCallback onTap) {
    return FilterChip(
      label: Text(label, style: TextStyle(fontSize: 13, color: selected ? Colors.white : null)),
      selected: selected,
      selectedColor: AppColors.primary,
      onSelected: (_) => onTap(),
    );
  }

  Widget _statusBadge(String status) {
    Color color;
    String label;
    switch (status) {
      case 'published': color = AppColors.secondary; label = 'منشور'; break;
      case 'draft': color = AppColors.gold; label = 'مسودة'; break;
      case 'archived': color = Colors.grey; label = 'مؤرشف'; break;
      default: color = Colors.grey; label = status;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
      decoration: BoxDecoration(color: color.withOpacity(0.12), borderRadius: BorderRadius.circular(6)),
      child: Text(label, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w500)),
    );
  }

  String _dateLabel(String? raw) {
    if (raw == null) return '';
    final dt = DateTime.tryParse(raw);
    return dt != null ? Helpers.timeAgo(dt) : '';
  }
}
