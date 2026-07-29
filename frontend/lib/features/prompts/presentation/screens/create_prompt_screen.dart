import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/utils/helpers.dart';
import '../../../core/utils/validators.dart';
import '../../../data/datasources/api_service.dart';
import '../../../data/repositories/prompt_repository.dart';
import '../../../domain/entities/prompt_model.dart';
import '../../../domain/entities/category_model.dart';
import '../../../domain/entities/ai_model_model.dart';

final createFormProviders = FutureProvider((ref) async {
  final repo = ref.read(promptRepositoryProvider);
  final categories = await repo.getCategories();
  final models = await repo.getModels();
  return (categories: categories, models: models);
});

class CreatePromptScreen extends ConsumerStatefulWidget {
  final PromptModel? editPrompt;
  const CreatePromptScreen({super.key, this.editPrompt});

  @override
  ConsumerState<CreatePromptScreen> createState() => _CreatePromptScreenState();
}

class _CreatePromptScreenState extends ConsumerState<CreatePromptScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleCtrl = TextEditingController();
  final _contentCtrl = TextEditingController();
  final _descCtrl = TextEditingController();
  String? _categoryId;
  String? _modelId;
  bool _isPublic = false;
  bool _isPremium = false;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    if (widget.editPrompt != null) {
      _titleCtrl.text = widget.editPrompt!.title;
      _contentCtrl.text = widget.editPrompt!.content;
      _descCtrl.text = widget.editPrompt!.description ?? '';
      _categoryId = widget.editPrompt!.categoryId;
      _modelId = widget.editPrompt!.modelId;
      _isPublic = widget.editPrompt!.isPublic;
      _isPremium = widget.editPrompt!.isPremium;
    }
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    _contentCtrl.dispose();
    _descCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final formData = ref.watch(createFormProviders);
    final colors = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: Text(widget.editPrompt != null ? 'تعديل البرومبت' : 'إنشاء برومبت جديد')),
      body: formData.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('$e')),
        data: (data) => SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TextFormField(
                  controller: _titleCtrl,
                  decoration: const InputDecoration(labelText: 'العنوان', prefixIcon: Icon(Icons.title)),
                  validator: (v) => Validators.required(v, 'العنوان'),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _contentCtrl,
                  decoration: const InputDecoration(labelText: 'المحتوى', prefixIcon: Icon(Icons.description), alignLabelWithHint: true),
                  maxLines: 8,
                  validator: (v) => Validators.required(v, 'المحتوى'),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _descCtrl,
                  decoration: const InputDecoration(labelText: 'الوصف (اختياري)', prefixIcon: Icon(Icons.info_outline), alignLabelWithHint: true),
                  maxLines: 3,
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: _categoryId,
                  decoration: const InputDecoration(labelText: 'التصنيف', prefixIcon: Icon(Icons.category)),
                  items: data.categories.map((c) => DropdownMenuItem(value: c.id, child: Text(c.nameAr ?? c.name))).toList(),
                  onChanged: (v) => setState(() => _categoryId = v),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: _modelId,
                  decoration: const InputDecoration(labelText: 'نموذج AI', prefixIcon: Icon(Icons.smart_toy)),
                  items: data.models.map((m) => DropdownMenuItem(value: m.id, child: Text('${m.name} (${m.provider})'))).toList(),
                  onChanged: (v) => setState(() => _modelId = v),
                ),
                const SizedBox(height: 16),
                SwitchListTile(
                  title: const Text('عام'),
                  subtitle: const Text('جعل البرومبت متاح للجميع'),
                  value: _isPublic,
                  onChanged: (v) => setState(() => _isPublic = v),
                ),
                SwitchListTile(
                  title: const Text('مميز (Premium)'),
                  subtitle: const Text('متاح فقط للمستخدمين المميزين'),
                  value: _isPremium,
                  onChanged: (v) => setState(() => _isPremium = v),
                ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: FilledButton(
                    onPressed: _saving ? null : _save,
                    child: _saving
                        ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                        : Text(widget.editPrompt != null ? 'حفظ التغييرات' : 'إنشاء البرومبت'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    try {
      final repo = ref.read(promptRepositoryProvider);
      final data = {
        'title': _titleCtrl.text,
        'content': _contentCtrl.text,
        'description': _descCtrl.text.isNotEmpty ? _descCtrl.text : null,
        'category_id': _categoryId,
        'model_id': _modelId,
        'is_public': _isPublic,
        'is_premium': _isPremium,
      };
      if (widget.editPrompt != null) {
        await repo.updatePrompt(widget.editPrompt!.id, data);
        Helpers.showToast('تم التحديث بنجاح');
      } else {
        await repo.createPrompt(data);
        Helpers.showToast('تم الإنشاء بنجاح');
      }
      if (mounted) context.pop();
    } catch (e) {
      Helpers.showToast('فشل: $e', isError: true);
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }
}
