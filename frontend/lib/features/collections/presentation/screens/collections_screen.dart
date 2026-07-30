import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/network/dio_client.dart';
import '../../../data/datasources/api_service.dart';
import '../../../domain/entities/collection_model.dart';

final collectionsProvider = FutureProvider((ref) async {
  final api = ApiService(ref.read(dioClientProvider));
  final response = await api.getList(ApiConstants.collections);
  if (response.data != null) {
    return response.data!.map((e) => CollectionModel.fromJson(e as Map<String, dynamic>)).toList();
  }
  return <CollectionModel>[];
});

class CollectionsScreen extends ConsumerWidget {
  const CollectionsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final collections = ref.watch(collectionsProvider);
    final colors = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('المجموعات')),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showCreateDialog(context, ref),
        child: const Icon(Icons.add),
      ),
      body: collections.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('$e')),
        data: (items) => items.isEmpty
            ? Center(child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.folder_open, size: 64, color: colors.onSurface.withValues(alpha: 0.3)),
                  const SizedBox(height: 16),
                  Text('لا توجد مجموعات', style: TextStyle(color: colors.onSurface.withValues(alpha: 0.5))),
                ],
              ))
            : RefreshIndicator(
                onRefresh: () async => ref.invalidate(collectionsProvider),
                child: GridView.builder(
                  padding: const EdgeInsets.all(16),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, childAspectRatio: 1.2, crossAxisSpacing: 12, mainAxisSpacing: 12),
                  itemCount: items.length,
                  itemBuilder: (_, i) => GestureDetector(
                    onTap: () => context.push('/collections/${items[i].id}'),
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Icon(Icons.folder, size: 40, color: colors.primary),
                            const Spacer(),
                            Text(items[i].name, style: const TextStyle(fontWeight: FontWeight.bold), maxLines: 1, overflow: TextOverflow.ellipsis),
                            const SizedBox(height: 4),
                            Text('${items[i].itemsCount ?? 0} عنصر', style: TextStyle(fontSize: 12, color: colors.onSurface.withValues(alpha: 0.5))),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
      ),
    );
  }

  void _showCreateDialog(BuildContext context, WidgetRef ref) {
    final nameController = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('مجموعة جديدة'),
        content: TextField(controller: nameController, decoration: const InputDecoration(labelText: 'اسم المجموعة'), autofocus: true),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('إلغاء')),
          FilledButton(
            onPressed: () async {
              if (nameController.text.isEmpty) return;
              final api = ApiService(ref.read(dioClientProvider));
              await api.post(ApiConstants.collections, data: {'name': nameController.text});
              if (ctx.mounted) Navigator.pop(ctx);
              ref.invalidate(collectionsProvider);
            },
            child: const Text('إنشاء'),
          ),
        ],
      ),
    );
  }
}
