class CategoryModel {
  final String id;
  final String name;
  final String? nameAr;
  final String slug;
  final String? description;
  final String? icon;
  final String? color;
  final int sortOrder;
  final bool isActive;
  final int? promptsCount;

  CategoryModel({
    required this.id, required this.name, this.nameAr, required this.slug,
    this.description, this.icon, this.color, this.sortOrder = 0,
    this.isActive = true, this.promptsCount,
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) {
    return CategoryModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      nameAr: json['name_ar'],
      slug: json['slug'] ?? '',
      description: json['description'],
      icon: json['icon'],
      color: json['color'],
      sortOrder: json['sort_order'] ?? 0,
      isActive: json['is_active'] ?? true,
      promptsCount: json['prompts_count'],
    );
  }
}
