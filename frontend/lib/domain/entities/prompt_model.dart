class PromptModel {
  final String id;
  final String? userId;
  final String title;
  final String? titleAr;
  final String content;
  final String? contentAr;
  final String? description;
  final String? descriptionAr;
  final String? modelId;
  final String? categoryId;
  final bool isPublic;
  final bool isPremium;
  final bool isTemplate;
  final int usageCount;
  final int copyCount;
  final double ratingAvg;
  final int ratingCount;
  final String status;
  final int version;
  final List<dynamic> tags;
  final String createdAt;
  final String? updatedAt;

  PromptModel({
    required this.id,
    this.userId,
    required this.title,
    this.titleAr,
    required this.content,
    this.contentAr,
    this.description,
    this.descriptionAr,
    this.modelId,
    this.categoryId,
    required this.isPublic,
    required this.isPremium,
    required this.isTemplate,
    this.usageCount = 0,
    this.copyCount = 0,
    this.ratingAvg = 0.0,
    this.ratingCount = 0,
    this.status = 'published',
    this.version = 1,
    this.tags = const [],
    required this.createdAt,
    this.updatedAt,
  });

  factory PromptModel.fromJson(Map<String, dynamic> json) {
    return PromptModel(
      id: json['id'] ?? '',
      userId: json['user_id']?.toString(),
      title: json['title'] ?? '',
      titleAr: json['title_ar'],
      content: json['content'] ?? '',
      contentAr: json['content_ar'],
      description: json['description'],
      descriptionAr: json['description_ar'],
      modelId: json['model_id']?.toString(),
      categoryId: json['category_id']?.toString(),
      isPublic: json['is_public'] ?? false,
      isPremium: json['is_premium'] ?? false,
      isTemplate: json['is_template'] ?? false,
      usageCount: json['usage_count'] ?? 0,
      copyCount: json['copy_count'] ?? 0,
      ratingAvg: (json['rating_avg'] ?? 0).toDouble(),
      ratingCount: json['rating_count'] ?? 0,
      status: json['status'] ?? 'published',
      version: json['version'] ?? 1,
      tags: json['tags'] ?? [],
      createdAt: json['created_at'] ?? '',
      updatedAt: json['updated_at'],
    );
  }
}
