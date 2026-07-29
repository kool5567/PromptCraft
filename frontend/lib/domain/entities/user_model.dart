class UserModel {
  final String id;
  final String email;
  final String username;
  final String role;
  final String subscriptionTier;
  final bool isActive;
  final bool isEmailVerified;
  final String? profileImage;
  final String? displayName;
  final String createdAt;
  final String? updatedAt;

  UserModel({
    required this.id,
    required this.email,
    required this.username,
    required this.role,
    required this.subscriptionTier,
    required this.isActive,
    required this.isEmailVerified,
    this.profileImage,
    this.displayName,
    required this.createdAt,
    this.updatedAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? '',
      email: json['email'] ?? '',
      username: json['username'] ?? '',
      role: json['role'] ?? 'user',
      subscriptionTier: json['subscription_tier'] ?? 'free',
      isActive: json['is_active'] ?? true,
      isEmailVerified: json['is_email_verified'] ?? false,
      profileImage: json['profile_image'],
      displayName: json['display_name'],
      createdAt: json['created_at'] ?? '',
      updatedAt: json['updated_at'],
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id, 'email': email, 'username': username, 'role': role,
    'subscription_tier': subscriptionTier, 'is_active': isActive,
    'is_email_verified': isEmailVerified, 'profile_image': profileImage,
    'display_name': displayName,
  };

  bool get isAdmin => role == 'admin' || role == 'superadmin';
  bool get isPremium => subscriptionTier != 'free';
}
