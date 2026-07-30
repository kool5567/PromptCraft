import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/api_constants.dart';
import '../../core/network/dio_client.dart';
import '../../domain/entities/prompt_model.dart';
import '../../domain/entities/category_model.dart';
import '../../domain/entities/ai_model_model.dart';
import '../datasources/api_service.dart';

final promptRepositoryProvider = Provider<PromptRepository>((ref) {
  return PromptRepository(ref.read(dioClientProvider));
});

class PromptRepository {
  final ApiService _api;
  PromptRepository(DioClient client) : _api = ApiService(client);

  Future<List<PromptModel>> getPublicPrompts({
    int page = 1, int size = 20, String? categoryId, String? modelId, String? search,
  }) async {
    final params = <String, dynamic>{'page': page, 'size': size};
    if (categoryId != null) params['category_id'] = categoryId;
    if (modelId != null) params['model_id'] = modelId;
    if (search != null) params['q'] = search;
    final response = await _api.getList(ApiConstants.library, params: params);
    if (response.isSuccess && response.data != null) {
      return response.data!.map((e) => PromptModel.fromJson(e as Map<String, dynamic>)).toList();
    }
    throw Exception(response.error ?? 'فشل تحميل البرومبتات');
  }

  Future<List<PromptModel>> getFeaturedPrompts({int limit = 10}) async {
    final response = await _api.getList('${ApiConstants.libraryFeatured}?limit=$limit');
    if (response.isSuccess && response.data != null) {
      return response.data!.map((e) => PromptModel.fromJson(e as Map<String, dynamic>)).toList();
    }
    return [];
  }

  Future<PromptModel> getPrompt(String id) async {
    final response = await _api.get(ApiConstants.prompt(id));
    if (response.isSuccess && response.data != null) {
      return PromptModel.fromJson(response.data!);
    }
    throw Exception(response.error ?? 'البرومبت غير موجود');
  }

  Future<PromptModel> createPrompt(Map<String, dynamic> data) async {
    final response = await _api.post(ApiConstants.prompts, data: data);
    if (response.isSuccess && response.data != null) {
      return PromptModel.fromJson(response.data!);
    }
    throw Exception(response.error ?? 'فشل إنشاء البرومبت');
  }

  Future<PromptModel> updatePrompt(String id, Map<String, dynamic> data) async {
    final response = await _api.put(ApiConstants.prompt(id), data: data);
    if (response.isSuccess && response.data != null) {
      return PromptModel.fromJson(response.data!);
    }
    throw Exception(response.error ?? 'فشل تحديث البرومبت');
  }

  Future<void> deletePrompt(String id) async {
    final response = await _api.delete(ApiConstants.prompt(id));
    if (!response.isSuccess) throw Exception(response.error ?? 'فشل حذف البرومبت');
  }

  Future<PromptModel> copyPrompt(String id) async {
    final response = await _api.post(ApiConstants.promptCopy(id));
    if (response.isSuccess && response.data != null) {
      return PromptModel.fromJson(response.data!);
    }
    throw Exception(response.error ?? 'فشل نسخ البرومبت');
  }

  Future<List<CategoryModel>> getCategories() async {
    final response = await _api.getList(ApiConstants.categories);
    if (response.isSuccess && response.data != null) {
      return response.data!.map((e) => CategoryModel.fromJson(e as Map<String, dynamic>)).toList();
    }
    return [];
  }

  Future<List<AiModelModel>> getModels({String? provider}) async {
    final path = provider != null ? '${ApiConstants.models}?provider=$provider' : ApiConstants.models;
    final response = await _api.getList(path);
    if (response.isSuccess && response.data != null) {
      return response.data!.map((e) => AiModelModel.fromJson(e as Map<String, dynamic>)).toList();
    }
    return [];
  }

  Future<List<PromptModel>> search(String query, {int page = 1, int size = 20, String? categoryId}) async {
    final params = <String, dynamic>{'q': query, 'page': page, 'size': size};
    if (categoryId != null) params['category_id'] = categoryId;
    final response = await _api.getList(ApiConstants.search, params: params);
    if (response.isSuccess && response.data != null) {
      return response.data!.map((e) => PromptModel.fromJson(e as Map<String, dynamic>)).toList();
    }
    return [];
  }
}
