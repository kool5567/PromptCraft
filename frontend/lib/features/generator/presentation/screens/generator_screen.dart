import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';

class GeneratorScreen extends ConsumerStatefulWidget {
  const GeneratorScreen({super.key});

  @override
  ConsumerState<GeneratorScreen> createState() => _GeneratorScreenState();
}

class _GeneratorScreenState extends ConsumerState<GeneratorScreen> {
  final _descriptionController = TextEditingController();
  String _selectedModel = 'ChatGPT';
  bool _isGenerating = false;
  String? _result;

  final _models = ['ChatGPT', 'Gemini', 'Claude', 'DeepSeek', 'Grok'];

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('مولد البرومبتات'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {},
            tooltip: 'السجل',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outlined, color: AppTheme.primaryColor),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'وصف ما تريد، وسيقوم الذكاء الاصطناعي بإنشاء برومبت احترافي لك',
                      style: TextStyle(color: AppTheme.primaryColor),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            Text('اختر النموذج', style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _selectedModel,
              decoration: const InputDecoration(prefixIcon: Icon(Icons.auto_awesome)),
              items: _models.map((m) => DropdownMenuItem(value: m, child: Text(m))).toList(),
              onChanged: (v) => setState(() => _selectedModel = v ?? 'ChatGPT'),
            ),
            const SizedBox(height: 20),
            Text('صف ما تحتاجه', style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 8),
            TextFormField(
              controller: _descriptionController,
              maxLines: 6,
              decoration: const InputDecoration(
                hintText: 'مثال: برومبت لكتابة مقالات تسويقية لمنتج جديد بأسلوب مقنع...',
                alignLabelWithHint: true,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _isGenerating ? null : _generate,
              icon: _isGenerating
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.auto_awesome),
              label: Text(_isGenerating ? 'جاري التوليد...' : 'توليد البرومبت'),
            ),
            if (_result != null) ...[
              const SizedBox(height: 24),
              Row(
                children: [
                  Text('النتيجة', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.copy),
                    onPressed: () {},
                    tooltip: 'نسخ',
                  ),
                  IconButton(
                    icon: const Icon(Icons.save_outlined),
                    onPressed: () {},
                    tooltip: 'حفظ',
                  ),
                  IconButton(
                    icon: const Icon(Icons.share_outlined),
                    onPressed: () {},
                    tooltip: 'مشاركة',
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: SelectableText(_result!, style: const TextStyle(fontFamily: 'monospace', fontSize: 14)),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Future<void> _generate() async {
    if (_descriptionController.text.trim().isEmpty) return;

    setState(() => _isGenerating = true);

    try {
      await Future.delayed(const Duration(seconds: 2));
      setState(() {
        _result = 'برومبت احترافي لـ $_selectedModel:\n\n'
            'أنت خبير في ${_descriptionController.text}. قم بـ:\n'
            '1. تحليل الموضوع بدقة\n'
            '2. تقديم حلول مبتكرة\n'
            '3. شرح كل خطوة بالتفصيل\n\n'
            'استخدم لغة واضحة ومنظمة مع أمثلة تطبيقية.';
      });
    } finally {
      setState(() => _isGenerating = false);
    }
  }
}
