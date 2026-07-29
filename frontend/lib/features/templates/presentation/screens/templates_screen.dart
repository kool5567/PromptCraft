import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/api_constants.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/utils/helpers.dart';
import '../../../../data/datasources/api_service.dart';
import '../../../../domain/entities/prompt_model.dart';

final templatesProvider = FutureProvider((ref) async {
  final api = ApiService(ref.read(dioClientProvider));
  final resp = await api.getList(ApiConstants.templates);
  if (resp.data != null) {
    return resp.data!.map((e) => PromptModel.fromJson(e as Map<String, dynamic>)).toList();
  }
  return <PromptModel>[];
});

class TemplatesScreen extends ConsumerWidget {
  const TemplatesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final templates = ref.watch(templatesProvider);
    final colors = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('القوالب')),
      body: templates.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('$e')),
        data: (items) => items.isEmpty
            ? Center(child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.widgets, size: 64, color: colors.onSurface.withValues(alpha: 0.3)),
                  const SizedBox(height: 16),
                  Text('لا توجد قوالب', style: TextStyle(color: colors.onSurface.withValues(alpha: 0.5))),
                ],
              ))
            : RefreshIndicator(
                onRefresh: () async => ref.invalidate(templatesProvider),
                child: GridView.builder(
                  padding: const EdgeInsets.all(16),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, childAspectRatio: 1.1, crossAxisSpacing: 12, mainAxisSpacing: 12),
                  itemCount: items.length,
                  itemBuilder: (_, i) => Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(items[i].title, style: const TextStyle(fontWeight: FontWeight.bold), maxLines: 2, overflow: TextOverflow.ellipsis),
                          const SizedBox(height: 4),
                          Text(items[i].description ?? '', maxLines: 2, overflow: TextOverflow.ellipsis,
                            style: TextStyle(fontSize: 12, color: colors.onSurface.withValues(alpha: 0.6))),
                          const Spacer(),
                          Text('${items[i].usageCount} استخدام', style: TextStyle(fontSize: 12, color: colors.onSurface.withValues(alpha: 0.5))),
                          const SizedBox(height: 8),
                          SizedBox(
                            width: double.infinity,
                            child: OutlinedButton(
                              onPressed: () async {
                                final api = ApiService(ref.read(dioClientProvider));
                                await api.post(ApiConstants.templateUse(items[i].id));
                                Helpers.showToast('تم نسخ القالب بنجاح');
                              },
                              child: const Text('استخدام'),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
      ),
    );
  }
}
