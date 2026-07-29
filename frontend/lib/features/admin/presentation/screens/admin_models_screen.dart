import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';

import '../../../../core/constants/api_constants.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/utils/helpers.dart';
import '../widgets/admin_drawer.dart';

class AdminModelsScreen extends ConsumerStatefulWidget {
  const AdminModelsScreen({super.key});

  @override
  ConsumerState<AdminModelsScreen> createState() => _AdminModelsScreenState();
}

class _AdminModelsScreenState extends ConsumerState<AdminModelsScreen> {
  List<Map<String, dynamic>> _models = [];
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
      final res = await dio.get(ApiConstants.models);
      setState(() {
        _models = (res.data is List ? res.data : res.data['models'] ?? []).cast<Map<String, dynamic>>();
      });
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _toggleActive(String id, bool currentlyActive) async {
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.put(ApiConstants.model(id), data: {'is_active': !currentlyActive});
      if (mounted) Helpers.showToast(!currentlyActive ? 'تم التفعيل' : 'تم الإيقاف');
      _fetch();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    }
  }

  Future<void> _save(Map<String, dynamic> data, {String? id}) async {
    try {
      final dio = ref.read(dioClientProvider).dio;
      if (id != null) {
        await dio.put(ApiConstants.model(id), data: data);
      } else {
        await dio.post(ApiConstants.models, data: data);
      }
      if (mounted) Helpers.showToast(id != null ? 'تم التحديث' : 'تمت الإضافة');
      _fetch();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    }
  }

  Future<void> _delete(String id, String name) async {
    final confirmed = await Helpers.showConfirmDialog(context, 'حذف النموذج', 'هل أنت متأكد من حذف النموذج "$name"؟');
    if (!confirmed) return;
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.delete(ApiConstants.model(id));
      if (mounted) Helpers.showToast('تم الحذف');
      _fetch();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('النماذج')),
      drawer: const AdminDrawer(currentRoute: '/admin/models'),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showDialog(),
        child: const Icon(Icons.add),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _models.isEmpty
              ? const Center(child: Text('لا توجد نماذج'))
              : RefreshIndicator(
                  onRefresh: _fetch,
                  child: ListView.builder(
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 80),
                    itemCount: _models.length,
                    itemBuilder: (_, i) {
                      final m = _models[i];
                      final active = m['is_active'] ?? true;
                      return Card(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: CircleAvatar(
                            radius: 18,
                            backgroundColor: active ? AppColors.primary.withOpacity(0.12) : Colors.grey.withOpacity(0.12),
                            child: Icon(Icons.memory, size: 20, color: active ? AppColors.primary : Colors.grey),
                          ),
                          title: Row(
                            children: [
                              Text(m['name'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                              const SizedBox(width: 8),
                              _providerBadge(m['provider'] ?? ''),
                            ],
                          ),
                          subtitle: Text(m['slug'] ?? '', style: const TextStyle(fontSize: 12)),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Switch(
                                value: active,
                                onChanged: (_) => _toggleActive(m['id'], active),
                                activeColor: AppColors.primary,
                              ),
                              IconButton(
                                icon: const Icon(Icons.edit_outlined, size: 20),
                                onPressed: () => _showDialog(model: m),
                              ),
                              IconButton(
                                icon: const Icon(Icons.delete_outline, size: 20, color: AppColors.error),
                                onPressed: () => _delete(m['id'], m['name']),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }

  Widget _providerBadge(String provider) {
    final colors = {
      'OpenAI': AppColors.primary,
      'Anthropic': AppColors.tertiary,
      'Google': const Color(0xFF3B82F6),
      'Meta': const Color(0xFF0F172A),
      'DeepSeek': const Color(0xFF10B981),
      'xAI': const Color(0xFFEC4899),
      'Mistral': const Color(0xFFF59E0B),
    };
    final color = colors[provider] ?? Colors.grey;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(color: color.withOpacity(0.12), borderRadius: BorderRadius.circular(6)),
      child: Text(provider, style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.w500)),
    );
  }

  void _showDialog({Map<String, dynamic>? model}) {
    final nameCtrl = TextEditingController(text: model?['name']);
    final slugCtrl = TextEditingController(text: model?['slug']);
    final descCtrl = TextEditingController(text: model?['description']);
    final providerCtrl = TextEditingController(text: model?['provider']);
    String category = model?['category'] ?? 'chat';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (_, setDialogState) => AlertDialog(
          title: Text(model != null ? 'تعديل نموذج' : 'إضافة نموذج جديد'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(controller: nameCtrl, decoration: const InputDecoration(labelText: 'الاسم', prefixIcon: Icon(Icons.title))),
                const SizedBox(height: 12),
                TextField(controller: slugCtrl, decoration: const InputDecoration(labelText: 'ال slug', prefixIcon: Icon(Icons.link))),
                const SizedBox(height: 12),
                TextField(controller: providerCtrl, decoration: const InputDecoration(labelText: 'المزود', prefixIcon: Icon(Icons.cloud))),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: category,
                  decoration: const InputDecoration(labelText: 'التصنيف', prefixIcon: Icon(Icons.category)),
                  items: ['chat', 'completion', 'image', 'embedding', 'code']
                      .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                      .toList(),
                  onChanged: (v) { if (v != null) setDialogState(() => category = v); },
                ),
                const SizedBox(height: 12),
                TextField(controller: descCtrl, decoration: const InputDecoration(labelText: 'الوصف', prefixIcon: Icon(Icons.description)), maxLines: 2),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('إلغاء')),
            FilledButton(
              onPressed: () {
                Navigator.pop(ctx);
                _save({
                  'name': nameCtrl.text, 'slug': slugCtrl.text, 'description': descCtrl.text,
                  'provider': providerCtrl.text, 'category': category,
                }, id: model?['id']);
              },
              child: const Text('حفظ'),
            ),
          ],
        ),
      ),
    );
  }
}
