import 'package:dio/dio.dart';
import '../../core/network/dio_client.dart';
import '../../domain/entities/user_model.dart';
import '../../domain/entities/prompt_model.dart';
import '../../domain/entities/category_model.dart';
import '../../domain/entities/ai_model_model.dart';

class ApiResponse<T> {
  final T? data;
  final String? error;
  final int? statusCode;

  ApiResponse({this.data, this.error, this.statusCode});

  bool get isSuccess => error == null && statusCode != null && statusCode! < 400;
}

class ApiService {
  final DioClient _client;
  ApiService(this._client);

  Dio get _dio => _client.dio;

  Future<ApiResponse<Map<String, dynamic>>> get(String path, {Map<String, dynamic>? params}) async {
    try {
      final response = await _dio.get(path, queryParameters: params);
      return ApiResponse(data: response.data is Map ? response.data as Map<String, dynamic> : {'data': response.data}, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResponse(error: _parseError(e), statusCode: e.response?.statusCode);
    }
  }

  Future<ApiResponse<List<dynamic>>> getList(String path, {Map<String, dynamic>? params}) async {
    try {
      final response = await _dio.get(path, queryParameters: params);
      final data = response.data;
      if (data is List) return ApiResponse(data: data, statusCode: response.statusCode);
      if (data is Map && data.containsKey('items')) return ApiResponse(data: data['items'], statusCode: response.statusCode);
      return ApiResponse(data: [], statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResponse(error: _parseError(e), statusCode: e.response?.statusCode);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> post(String path, {dynamic data}) async {
    try {
      final response = await _dio.post(path, data: data);
      return ApiResponse(data: response.data is Map ? response.data as Map<String, dynamic> : {'data': response.data}, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResponse(error: _parseError(e), statusCode: e.response?.statusCode);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> put(String path, {dynamic data}) async {
    try {
      final response = await _dio.put(path, data: data);
      return ApiResponse(data: response.data is Map ? response.data as Map<String, dynamic> : {'data': response.data}, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResponse(error: _parseError(e), statusCode: e.response?.statusCode);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> delete(String path) async {
    try {
      final response = await _dio.delete(path);
      return ApiResponse(data: response.data is Map ? response.data as Map<String, dynamic> : {'data': response.data}, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResponse(error: _parseError(e), statusCode: e.response?.statusCode);
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> uploadFile(String path, String filePath, {Map<String, dynamic>? fields}) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath),
        if (fields != null) ...fields,
      });
      final response = await _dio.post(path, data: formData);
      return ApiResponse(data: response.data is Map ? response.data as Map<String, dynamic> : {'data': response.data}, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResponse(error: _parseError(e), statusCode: e.response?.statusCode);
    }
  }

  String _parseError(DioException e) {
    if (e.response?.data is Map) {
      return (e.response!.data as Map)['detail']?.toString() ?? (e.response!.data as Map)['message']?.toString() ?? 'حدث خطأ';
    }
    return e.message ?? 'حدث خطأ في الاتصال';
  }
}
