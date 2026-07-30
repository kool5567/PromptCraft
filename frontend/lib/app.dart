import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'features/core/theme/app_theme.dart';
import 'features/core/storage/secure_storage.dart';
import 'features/data/repositories/auth_repository.dart';
import 'features/auth/presentation/screens/login_screen.dart';
import 'features/auth/presentation/screens/register_screen.dart';
import 'features/home/presentation/screens/home_screen.dart';
import 'features/library/presentation/screens/library_screen.dart';
import 'features/prompts/presentation/screens/prompt_list_screen.dart';
import 'features/prompts/presentation/screens/prompt_detail_screen.dart';
import 'features/prompts/presentation/screens/create_prompt_screen.dart';
import 'features/prompts/presentation/screens/edit_prompt_screen.dart';
import 'features/generator/presentation/screens/generator_screen.dart';
import 'features/collections/presentation/screens/collections_screen.dart';
import 'features/collections/presentation/screens/collection_detail_screen.dart';
import 'features/favorites/presentation/screens/favorites_screen.dart';
import 'features/templates/presentation/screens/templates_screen.dart';
import 'features/profile/presentation/screens/profile_screen.dart';
import 'features/settings/presentation/screens/settings_screen.dart';
import 'features/subscription/presentation/screens/subscription_screen.dart';
import 'features/subscription/presentation/screens/plans_screen.dart';
import 'features/admin/presentation/screens/admin_dashboard_screen.dart';
import 'features/admin/presentation/screens/admin_users_screen.dart';
import 'features/admin/presentation/screens/admin_prompts_screen.dart';
import 'features/admin/presentation/screens/admin_categories_screen.dart';
import 'features/admin/presentation/screens/admin_models_screen.dart';
import 'features/admin/presentation/screens/admin_imports_screen.dart';
import 'features/admin/presentation/screens/admin_settings_screen.dart';
import 'features/admin/presentation/screens/admin_analytics_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authRepo = ref.read(authRepositoryProvider);
  return GoRouter(
    initialLocation: '/',
    redirect: (context, state) async {
      final loggedIn = await authRepo.isLoggedIn();
      final isAuthRoute = state.matchedLocation.startsWith('/login') || state.matchedLocation.startsWith('/register');
      if (loggedIn && isAuthRoute) return '/';
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
      GoRoute(path: '/', builder: (_, __) => const HomeScreen()),
      GoRoute(path: '/prompts', builder: (_, __) => const PromptListScreen()),
      GoRoute(path: '/prompts/new', builder: (_, __) => const CreatePromptScreen()),
GoRoute(path: '/prompts/:id', builder: (_, state) => PromptDetailScreen(id: state.pathParameters['id']!)),
GoRoute(path: '/prompts/:id/edit', builder: (_, state) => EditPromptScreen(promptId: state.pathParameters['id']!)),
      GoRoute(path: '/generator', builder: (_, __) => const GeneratorScreen()),
      GoRoute(path: '/library', builder: (_, __) => const LibraryScreen()),
      GoRoute(path: '/collections', builder: (_, __) => const CollectionsScreen()),
      GoRoute(path: '/collections/:id', builder: (_, state) => CollectionDetailScreen(collectionId: state.pathParameters['id']!)),
      GoRoute(path: '/favorites', builder: (_, __) => const FavoritesScreen()),
      GoRoute(path: '/templates', builder: (_, __) => const TemplatesScreen()),
      GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
      GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),
      GoRoute(path: '/subscription', builder: (_, __) => const SubscriptionScreen()),
      GoRoute(path: '/subscription/plans', builder: (_, __) => const PlansScreen()),
      GoRoute(path: '/admin', builder: (_, __) => const AdminDashboardScreen()),
      GoRoute(path: '/admin/users', builder: (_, __) => const AdminUsersScreen()),
      GoRoute(path: '/admin/prompts', builder: (_, __) => const AdminPromptsScreen()),
      GoRoute(path: '/admin/categories', builder: (_, __) => const AdminCategoriesScreen()),
      GoRoute(path: '/admin/models', builder: (_, __) => const AdminModelsScreen()),
      GoRoute(path: '/admin/imports', builder: (_, __) => const AdminImportsScreen()),
      GoRoute(path: '/admin/settings', builder: (_, __) => const AdminSettingsScreen()),
      GoRoute(path: '/admin/analytics', builder: (_, __) => const AdminAnalyticsScreen()),
    ],
  );
});
