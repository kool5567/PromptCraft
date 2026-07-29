import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_theme.dart';
import '../../../data/repositories/auth_repository.dart';
import '../../../data/repositories/prompt_repository.dart';
import '../../../domain/entities/prompt_model.dart';
import '../../../domain/entities/category_model.dart';

final homeDataProvider = FutureProvider((ref) async {
  final promptRepo = ref.read(promptRepositoryProvider);
  final authRepo = ref.read(authRepositoryProvider);
  final user = await authRepo.getCachedUser();
  final featured = await promptRepo.getFeaturedPrompts(limit: 10);
  final categories = await promptRepo.getCategories();
  return (user: user, featured: featured, categories: categories);
});

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final homeData = ref.watch(homeDataProvider);
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      body: homeData.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('حدث خطأ: $e')),
        data: (data) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(homeDataProvider),
          child: CustomScrollView(
            slivers: [
              SliverAppBar(
                expandedHeight: 140,
                floating: false, pinned: true,
                flexibleSpace: FlexibleSpaceBar(
                  background: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(colors: [colorScheme.primary, colorScheme.primary.withValues(alpha: 0.8)]),
                    ),
                    padding: const EdgeInsets.fromLTRB(20, 60, 20, 20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Text('مرحباً! 👋', style: TextStyle(color: Colors.white70, fontSize: 14)),
                        const SizedBox(height: 4),
                        Text(data.user?.displayName ?? data.user?.username ?? 'مستخدم',
                          style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ),
                ),
                actions: [
                  IconButton(icon: const Icon(Icons.settings), onPressed: () => context.push('/settings')),
                ],
              ),
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildQuickActions(context, colorScheme),
                      const SizedBox(height: 24),
                      Text('البرومبتات المميزة', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: colorScheme.onSurface)),
                      const SizedBox(height: 12),
                      SizedBox(
                        height: 200,
                        child: data.featured.isEmpty
                            ? Center(child: Text('لا توجد برومبتات مميزة', style: TextStyle(color: colorScheme.onSurface.withValues(alpha: 0.5))))
                            : ListView.builder(
                                scrollDirection: Axis.horizontal,
                                itemCount: data.featured.length,
                                itemBuilder: (_, i) => _buildFeaturedCard(context, data.featured[i], colorScheme),
                              ),
                      ),
                      const SizedBox(height: 24),
                      Text('التصنيفات', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: colorScheme.onSurface)),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 8, runSpacing: 8,
                        children: data.categories.map((c) => _buildCategoryChip(context, c, colorScheme)).toList(),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickActions(BuildContext context, ColorScheme colors) {
    return Row(
      children: [
        Expanded(child: _ActionCard(icon: Icons.add, label: 'برومبت جديد', color: colors.primary, onTap: () => context.push('/prompts/new'))),
        const SizedBox(width: 12),
        Expanded(child: _ActionCard(icon: Icons.auto_awesome, label: 'المولد', color: colors.secondary, onTap: () => context.push('/generator'))),
        const SizedBox(width: 12),
        Expanded(child: _ActionCard(icon: Icons.folder, label: 'مكتبتي', color: colors.tertiary, onTap: () => context.push('/library'))),
      ],
    );
  }

  Widget _buildFeaturedCard(BuildContext context, PromptModel prompt, ColorScheme colors) {
    return GestureDetector(
      onTap: () => context.push('/prompts/${prompt.id}'),
      child: Container(
        width: 180, margin: const EdgeInsets.only(left: 12),
        decoration: BoxDecoration(
          color: colors.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(16),
        ),
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(prompt.title, maxLines: 2, overflow: TextOverflow.ellipsis,
              style: TextStyle(fontWeight: FontWeight.w600, color: colors.onSurface)),
            const Spacer(),
            Row(
              children: [
                Icon(Icons.star, size: 16, color: Colors.amber),
                const SizedBox(width: 4),
                Text(prompt.ratingAvg.toString(), style: TextStyle(color: colors.onSurface.withValues(alpha: 0.7))),
                const Spacer(),
                Text('${prompt.usageCount}', style: TextStyle(fontSize: 12, color: colors.onSurface.withValues(alpha: 0.5))),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCategoryChip(BuildContext context, CategoryModel category, ColorScheme colors) {
    return ActionChip(
      avatar: Icon(category.icon != null ? Icons.category : Icons.folder, size: 18),
      label: Text(category.nameAr ?? category.name),
      onPressed: () => context.push('/library'),
    );
  }
}

class _ActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionCard({required this.icon, required this.label, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: color.withValues(alpha: 0.1),
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 12),
          child: Column(
            children: [
              Icon(icon, color: color, size: 28),
              const SizedBox(height: 8),
              Text(label, style: TextStyle(color: color, fontWeight: FontWeight.w600, fontSize: 13)),
            ],
          ),
        ),
      ),
    );
  }
}
