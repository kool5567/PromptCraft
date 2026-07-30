class CollectionModel {
  final String id;
  final String userId;
  final String name;
  final String? nameAr;
  final String? description;
  final bool isPublic;
  final String? coverImage;
  final int sortOrder;
  final int? itemsCount;
  final String createdAt;
  final String? updatedAt;

  CollectionModel({
    required this.id, required this.userId, required this.name, this.nameAr,
    this.description, this.isPublic = false, this.coverImage, this.sortOrder = 0,
    this.itemsCount, required this.createdAt, this.updatedAt,
  });

  factory CollectionModel.fromJson(Map<String, dynamic> json) {
    return CollectionModel(
      id: json['id'] ?? '', userId: json['user_id'] ?? '', name: json['name'] ?? '',
      nameAr: json['name_ar'], description: json['description'],
      isPublic: json['is_public'] ?? false, coverImage: json['cover_image'],
      sortOrder: json['sort_order'] ?? 0, itemsCount: json['items_count'],
      createdAt: json['created_at'] ?? '', updatedAt: json['updated_at'],
    );
  }
}
