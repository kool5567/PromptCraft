class ApiConstants {
  static const String baseUrl = 'https://web-production-4a7775.up.railway.app';
  static const String apiPrefix = '/api/v1';

  static const String login = '$apiPrefix/auth/login';
  static const String register = '$apiPrefix/auth/register';
  static const String refreshToken = '$apiPrefix/auth/refresh';
  static const String forgotPassword = '$apiPrefix/auth/forgot-password';
  static const String resetPassword = '$apiPrefix/auth/reset-password';
  static const String profile = '$apiPrefix/auth/profile';

  static const String userMe = '$apiPrefix/users/me';
  static const String userStats = '$apiPrefix/users/me/stats';
  static const String userPassword = '$apiPrefix/users/me/password';

  static const String prompts = '$apiPrefix/prompts';
  static String prompt(String id) => '$apiPrefix/prompts/$id';
  static String promptCopy(String id) => '$apiPrefix/prompts/$id/copy';
  static String promptRate(String id) => '$apiPrefix/prompts/$id/rate';
  static String promptRatings(String id) => '$apiPrefix/prompts/$id/ratings';

  static const String generatorGenerate = '$apiPrefix/generator/generate';
  static const String generatorEnhance = '$apiPrefix/generator/enhance';
  static const String generatorTranslate = '$apiPrefix/generator/translate';

  static const String library = '$apiPrefix/library';
  static const String libraryFeatured = '$apiPrefix/library/featured';
  static const String libraryRecent = '$apiPrefix/library/recent';
  static const String libraryPopular = '$apiPrefix/library/popular';

  static const String categories = '$apiPrefix/categories';
  static String category(String slug) => '$apiPrefix/categories/$slug';
  static String categoryPrompts(String slug) => '$apiPrefix/categories/$slug/prompts';

  static const String tags = '$apiPrefix/tags';
  static String tag(String slug) => '$apiPrefix/tags/$slug';

  static const String models = '$apiPrefix/models';
  static String model(String slug) => '$apiPrefix/models/$slug';

  static const String favorites = '$apiPrefix/favorites';
  static String favorite(String promptId) => '$apiPrefix/favorites/$promptId';

  static const String collections = '$apiPrefix/collections';
  static String collection(String id) => '$apiPrefix/collections/$id';
  static String collectionPrompts(String id) => '$apiPrefix/collections/$id/prompts';
  static String collectionRemovePrompt(String collId, String promptId) =>
      '$apiPrefix/collections/$collId/prompts/$promptId';

  static const String templates = '$apiPrefix/templates';
  static String template(String id) => '$apiPrefix/templates/$id';
  static String templateUse(String id) => '$apiPrefix/templates/$id/use';

  static const String search = '$apiPrefix/search';
  static const String searchSuggestions = '$apiPrefix/search/suggestions';

  static const String subscriptionPlans = '$apiPrefix/subscriptions/plans';
  static const String subscriptionMy = '$apiPrefix/subscriptions/my';
  static const String subscriptionSubscribe = '$apiPrefix/subscriptions/subscribe';
  static const String subscriptionCancel = '$apiPrefix/subscriptions/cancel';
  static const String subscriptionChangePlan = '$apiPrefix/subscriptions/change-plan';

  static const String importGithub = '$apiPrefix/import/github';
  static const String importFile = '$apiPrefix/import/file';
  static const String importJobs = '$apiPrefix/import/jobs';
  static String importJob(String id) => '$apiPrefix/import/jobs/$id';
  static const String exportPrompts = '$apiPrefix/export/prompts';
  static String exportCollection(String id) => '$apiPrefix/export/collection/$id';

  static const String adminDashboard = '$apiPrefix/admin/dashboard';
  static const String adminUsers = '$apiPrefix/admin/users';
  static String adminUser(String id) => '$apiPrefix/admin/users/$id';
  static const String adminPrompts = '$apiPrefix/admin/prompts';
  static String adminPromptStatus(String id) => '$apiPrefix/admin/prompts/$id/status';
  static const adminImports = '$apiPrefix/admin/imports';
  static const String adminSettings = '$apiPrefix/admin/settings';
  static const String adminAnalytics = '$apiPrefix/admin/analytics';
  static const String adminLogs = '$apiPrefix/admin/logs';
  static const String adminSyncGithub = '$apiPrefix/admin/sync-github';
  static const String adminSeedModels = '$apiPrefix/admin/seed-models';
  static const String adminSeedCategories = '$apiPrefix/admin/seed-categories';

  static const String health = '/health';
}
