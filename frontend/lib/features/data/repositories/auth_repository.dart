import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/api_constants.dart';
import '../../core/network/dio_client.dart';
import '../../core/storage/secure_storage.dart';
import '../../domain/entities/user_model.dart';
import '../datasources/api_service.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.read(dioClientProvider), ref.read(secureStorageProvider));
});

class AuthRepository {
  final ApiService _api;
  final SecureStorageService _storage;

  AuthRepository(DioClient client, this._storage) : _api = ApiService(client);

  Future<UserModel?> login(String email, String password) async {
    final response = await _api.post(ApiConstants.login, data: {'email': email, 'password': password});
    if (response.isSuccess && response.data != null) {
      await _storage.saveToken(response.data!['access_token'] ?? response.data!['token']);
      if (response.data!['refresh_token'] != null) {
        await _storage.saveRefreshToken(response.data!['refresh_token']);
      }
      final user = UserModel.fromJson(response.data!['user'] ?? response.data!);
      await _storage.saveUser(jsonEncode(user.toJson()));
      return user;
    }
    throw Exception(response.error ?? 'فشل تسجيل الدخول');
  }

  Future<UserModel?> register(String username, String email, String password) async {
    final response = await _api.post(ApiConstants.register, data: {
      'username': username, 'email': email, 'password': password,
    });
    if (response.isSuccess && response.data != null) {
      await _storage.saveToken(response.data!['access_token'] ?? response.data!['token']);
      if (response.data!['refresh_token'] != null) {
        await _storage.saveRefreshToken(response.data!['refresh_token']);
      }
      final user = UserModel.fromJson(response.data!['user'] ?? response.data!);
      await _storage.saveUser(jsonEncode(user.toJson()));
      return user;
    }
    throw Exception(response.error ?? 'فشل التسجيل');
  }

  Future<UserModel?> getProfile() async {
    final response = await _api.get(ApiConstants.userMe);
    if (response.isSuccess && response.data != null) {
      final user = UserModel.fromJson(response.data!);
      await _storage.saveUser(jsonEncode(user.toJson()));
      return user;
    }
    final cached = await _storage.getUser();
    if (cached != null) return UserModel.fromJson(jsonDecode(cached));
    return null;
  }

  Future<void> logout() async {
    await _storage.clear();
  }

  Future<UserModel?> getCachedUser() async {
    final cached = await _storage.getUser();
    if (cached != null) return UserModel.fromJson(jsonDecode(cached));
    return null;
  }

  Future<bool> isLoggedIn() async {
    final token = await _storage.getToken();
    return token != null && token.isNotEmpty;
  }
}
