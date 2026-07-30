import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/network/dio_client.dart';
import '../../../data/datasources/api_service.dart';
import '../../../domain/entities/prompt_model.dart';

final collectionDetailProvider = FutureProvider.family((ref, String id) async {
  final api = ApiService(ref.read(dioClientProvider));
  final resp = await api.get(ApiConstants.collection(id));
  final promptsResp = await api.getList('${ApiConstants.collection(id)}/prompts');
  return (
    collection: resp.data,
    prompts: promptsResp.data?.map((e) => PromptModel.fromJson(e as Map<String, dynamic>)).toList() ?? <PromptModel>[],
  );
});

class CollectionDetailScreen extends ConsumerWidget {
  final String collectionId;
  const CollectionDetailScreen({super.key, required this.collectionId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(collectionDetailProvider(collectionId));
    final colors = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: data.value?.collection?['name']?.toString() != null ? Text(data.value!.collection!['name']) : null,
        actions: [
          IconButton(icon: const Icon(Icons.delete_outline), onPressed: () async {
            final api = ApiService(ref.read(dioClientProvider));
            await api.delete(ApiConstants.collection(collectionId));
            if (context.mounted) context.pop();
          }),
        ],
      ),
      body: data.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('$e')),
        data: (d) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(collectionDetailProvider(collectionId)),
          child: d.prompts.isEmpty
              ? Center(child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.inbox, size: 64, color: colors.onSurface.withValues(alpha: 0.3)),
                    const SizedBox(height: 16),
                    Text('المجموعة فارغة', style: TextStyle(color: colors.onSurface.withValues(alpha: 0.5))),
                  ],
                ))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: d.prompts.length,
                  itemBuilder: (_, i) => Card(
                    child: ListTile(
                      title: Text(d.prompts[i].title),
                      subtitle: Text(d.prompts[i].description ?? '', maxLines: 2, overflow: TextOverflow.ellipsis),
                      trailing: IconButton(
                        icon: const Icon(Icons.remove_circle_outline, color: Colors.red),
                        onPressed: () async {
                          final api = ApiService(ref.read(dioClientProvider));
                          await api.delete(ApiConstants.collectionRemovePrompt(collectionId, d.prompts[i].id));
                          ref.invalidate(collectionDetailProvider(collectionId));
                        },
                      ),
                      onTap: () => context.push('/prompts/${d.prompts[i].id}'),
                    ),
                  ),
                ),
        ),
      ),
    );
  }
}
