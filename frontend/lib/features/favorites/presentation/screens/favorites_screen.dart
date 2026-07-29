import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/network/dio_client.dart';
import '../../../data/datasources/api_service.dart';
import '../../../domain/entities/prompt_model.dart';

final favoritesProvider = FutureProvider((ref) async {
  final api = ApiService(ref.read(dioClientProvider));
  final resp = await api.getList(ApiConstants.favorites);
  if (resp.data != null) {
    return resp.data!.map((e) {
      final promptData = e is Map ? (e['prompt'] ?? e) : e;
      return PromptModel.fromJson(promptData as Map<String, dynamic>);
    }).toList();
  }
  return <PromptModel>[];
});

class FavoritesScreen extends ConsumerWidget {
  const FavoritesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final favorites = ref.watch(favoritesProvider);
    final colors = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('المفضلة')),
      body: favorites.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('$e')),
        data: (items) => items.isEmpty
            ? Center(child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.favorite_border, size: 64, color: colors.onSurface.withValues(alpha: 0.3)),
                  const SizedBox(height: 16),
                  Text('لا توجد برومبتات مفضلة', style: TextStyle(color: colors.onSurface.withValues(alpha: 0.5))),
                ],
              ))
            : RefreshIndicator(
                onRefresh: () async => ref.invalidate(favoritesProvider),
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: items.length,
                  itemBuilder: (_, i) => Card(
                    child: ListTile(
                      title: Text(items[i].title, maxLines: 1, overflow: TextOverflow.ellipsis),
                      subtitle: Row(
                        children: [
                          Icon(Icons.star, size: 14, color: Colors.amber),
                          const SizedBox(width: 4),
                          Text(items[i].ratingAvg.toString()),
                          const SizedBox(width: 12),
                          Text('${items[i].usageCount} استخدام'),
                        ],
                      ),
                      trailing: IconButton(
                        icon: Icon(Icons.favorite, color: Colors.red.shade400),
                        onPressed: () async {
                          final api = ApiService(ref.read(dioClientProvider));
                          await api.delete(ApiConstants.favorite(items[i].id));
                          ref.invalidate(favoritesProvider);
                        },
                      ),
                      onTap: () => context.push('/prompts/${items[i].id}'),
                    ),
                  ),
                ),
              ),
      ),
    );
  }
}
