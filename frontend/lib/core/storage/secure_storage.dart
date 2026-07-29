import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final secureStorageProvider = Provider<SecureStorageService>((ref) {
  return SecureStorageService();
});

class SecureStorageService {
  final _storage = const FlutterSecureStorage();

  static const _tokenKey = 'auth_token';
  static const _refreshTokenKey = 'refresh_token';
  static const _userKey = 'user_data';
  static const _themeKey = 'theme_mode';

  Future<void> saveToken(String token) => _storage.write(key: _tokenKey, value: token);
  Future<String?> getToken() => _storage.read(key: _tokenKey);
  Future<void> deleteToken() => _storage.delete(key: _tokenKey);

  Future<void> saveRefreshToken(String token) => _storage.write(key: _refreshTokenKey, value: token);
  Future<String?> getRefreshToken() => _storage.read(key: _refreshTokenKey);
  Future<void> deleteRefreshToken() => _storage.delete(key: _refreshTokenKey);

  Future<void> saveUser(String userJson) => _storage.write(key: _userKey, value: userJson);
  Future<String?> getUser() => _storage.read(key: _userKey);
  Future<void> deleteUser() => _storage.delete(key: _userKey);

  Future<void> saveThemeMode(String mode) => _storage.write(key: _themeKey, value: mode);
  Future<String?> getThemeMode() => _storage.read(key: _themeKey);

  Future<void> clear() async {
    await _storage.deleteAll();
  }
}
