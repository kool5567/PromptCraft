class AiModelModel {
  final String id;
  final String name;
  final String slug;
  final String? description;
  final String provider;
  final String category;
  final String? logoUrl;
  final bool isActive;
  final int sortOrder;

  AiModelModel({
    required this.id, required this.name, required this.slug,
    this.description, required this.provider, required this.category,
    this.logoUrl, this.isActive = true, this.sortOrder = 0,
  });

  factory AiModelModel.fromJson(Map<String, dynamic> json) {
    return AiModelModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      slug: json['slug'] ?? '',
      description: json['description'],
      provider: json['provider'] ?? '',
      category: json['category'] ?? '',
      logoUrl: json['logo_url'],
      isActive: json['is_active'] ?? true,
      sortOrder: json['sort_order'] ?? 0,
    );
  }
}
