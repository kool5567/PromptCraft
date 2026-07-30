import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';

import '../../../core/constants/api_constants.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/helpers.dart';
import '../widgets/admin_drawer.dart';

class AdminCategoriesScreen extends ConsumerStatefulWidget {
  const AdminCategoriesScreen({super.key});

  @override
  ConsumerState<AdminCategoriesScreen> createState() => _AdminCategoriesScreenState();
}

class _AdminCategoriesScreenState extends ConsumerState<AdminCategoriesScreen> {
  List<Map<String, dynamic>> _categories = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetch();
  }

  Future<void> _fetch() async {
    setState(() => _loading = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      final res = await dio.get(ApiConstants.categories);
      setState(() {
        _categories = (res.data is List ? res.data : res.data['categories'] ?? [])
            .cast<Map<String, dynamic>>();
      });
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _save(Map<String, dynamic> data, {String? id}) async {
    try {
      final dio = ref.read(dioClientProvider).dio;
      if (id != null) {
        await dio.put(ApiConstants.category(id), data: data);
      } else {
        await dio.post(ApiConstants.categories, data: data);
      }
      if (mounted) Helpers.showToast(id != null ? 'تم التحديث' : 'تمت الإضافة');
      _fetch();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    }
  }

  Future<void> _delete(String id, String name) async {
    final confirmed = await Helpers.showConfirmDialog(context, 'حذف التصنيف', 'هل أنت متأكد من حذف التصنيف "$name"؟');
    if (!confirmed) return;
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.delete(ApiConstants.category(id));
      if (mounted) Helpers.showToast('تم الحذف');
      _fetch();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    }
  }

  Future<void> _reorder(int oldI, int newI) async {
    setState(() {
      final item = _categories.removeAt(oldI);
      _categories.insert(newI, item);
    });
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.put(ApiConstants.categories, data: {
        'ordered_ids': _categories.map((c) => c['id']).toList(),
      });
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'خطأ في حفظ الترتيب', isError: true);
      _fetch();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('التصنيفات')),
      drawer: const AdminDrawer(currentRoute: '/admin/categories'),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showDialog(),
        child: const Icon(Icons.add),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _categories.isEmpty
              ? const Center(child: Text('لا توجد تصنيفات'))
              : RefreshIndicator(
                  onRefresh: _fetch,
                  child: ReorderableListView.builder(
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 80),
                    itemCount: _categories.length,
                    onReorder: _reorder,
                    itemBuilder: (_, i) {
                      final c = _categories[i];
                      final iconData = _iconFromString(c['icon']);
                      final color = _colorFromString(c['color']);
                      return Card(
                        key: ValueKey(c['id'] ?? c['slug']),
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(color: color.withOpacity(0.12), borderRadius: BorderRadius.circular(8)),
                            child: Icon(iconData, color: color, size: 20),
                          ),
                          title: Text(c['name'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                          subtitle: Text('${c['slug'] ?? ''} • ${c['prompts_count'] ?? 0} برومبت', style: const TextStyle(fontSize: 12)),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              IconButton(icon: const Icon(Icons.edit_outlined, size: 20), onPressed: () => _showDialog(category: c)),
                              IconButton(
                                icon: const Icon(Icons.delete_outline, size: 20, color: AppColors.error),
                                onPressed: () => _delete(c['id'], c['name']),
                              ),
                              const Icon(Icons.drag_handle, color: Colors.grey),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }

  void _showDialog({Map<String, dynamic>? category}) {
    final nameCtrl = TextEditingController(text: category?['name']);
    final nameArCtrl = TextEditingController(text: category?['name_ar']);
    final slugCtrl = TextEditingController(text: category?['slug']);
    final descCtrl = TextEditingController(text: category?['description']);
    String selectedIcon = category?['icon'] ?? 'category';
    String selectedColor = category?['color'] ?? '#6366F1';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (_, setDialogState) => AlertDialog(
          title: Text(category != null ? 'تعديل تصنيف' : 'إضافة تصنيف جديد'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(controller: nameCtrl, decoration: const InputDecoration(labelText: 'الاسم', prefixIcon: Icon(Icons.text_fields))),
                const SizedBox(height: 12),
                TextField(controller: nameArCtrl, decoration: const InputDecoration(labelText: 'الاسم (عربي)', prefixIcon: Icon(Icons.language))),
                const SizedBox(height: 12),
                TextField(controller: slugCtrl, decoration: const InputDecoration(labelText: 'ال slug', prefixIcon: Icon(Icons.link))),
                const SizedBox(height: 12),
                TextField(controller: descCtrl, decoration: const InputDecoration(labelText: 'الوصف', prefixIcon: Icon(Icons.description)), maxLines: 2),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: selectedIcon,
                  decoration: const InputDecoration(labelText: 'الأيقونة', prefixIcon: Icon(Icons.emoji_symbols)),
                  items: ['category', 'code', 'edit', 'business', 'school', 'campaign', 'analytics', 'palette', 'science', 'music_note']
                      .map((ic) => DropdownMenuItem(value: ic, child: Row(children: [Icon(_iconFromString(ic), size: 18), const SizedBox(width: 8), Text(ic)])))
                      .toList(),
                  onChanged: (v) { if (v != null) setDialogState(() => selectedIcon = v); },
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: selectedColor,
                  decoration: const InputDecoration(labelText: 'اللون', prefixIcon: Icon(Icons.colorize)),
                  items: ['#6366F1', '#14B8A6', '#EF4444', '#F59E0B', '#8B5CF6', '#3B82F6', '#EC4899', '#10B981']
                      .map((cl) => DropdownMenuItem(
                        value: cl,
                        child: Row(children: [Container(width: 18, height: 18, decoration: BoxDecoration(color: _colorFromString(cl), shape: BoxShape.circle)), const SizedBox(width: 8), Text(cl)]),
                      ))
                      .toList(),
                  onChanged: (v) { if (v != null) setDialogState(() => selectedColor = v); },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('إلغاء')),
            FilledButton(
              onPressed: () {
                Navigator.pop(ctx);
                _save({
                  'name': nameCtrl.text, 'name_ar': nameArCtrl.text, 'slug': slugCtrl.text,
                  'description': descCtrl.text, 'icon': selectedIcon, 'color': selectedColor,
                }, id: category?['id']);
              },
              child: const Text('حفظ'),
            ),
          ],
        ),
      ),
    );
  }

  IconData _iconFromString(String? icon) {
    switch (icon) {
      case 'code': return Icons.code;
      case 'edit': return Icons.edit;
      case 'business': return Icons.business;
      case 'school': return Icons.school;
      case 'campaign': return Icons.campaign;
      case 'analytics': return Icons.analytics;
      case 'palette': return Icons.palette;
      case 'science': return Icons.science;
      case 'music_note': return Icons.music_note;
      default: return Icons.category;
    }
  }

  Color _colorFromString(String? color) {
    if (color == null) return AppColors.primary;
    final hex = color.replaceFirst('#', '');
    if (hex.length == 6) {
      return Color(int.parse('FF$hex', radix: 16));
    }
    return AppColors.primary;
  }
}
