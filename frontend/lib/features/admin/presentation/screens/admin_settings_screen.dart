import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';

import '../../../core/constants/api_constants.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/helpers.dart';
import '../widgets/admin_drawer.dart';

class AdminSettingsScreen extends ConsumerStatefulWidget {
  const AdminSettingsScreen({super.key});

  @override
  ConsumerState<AdminSettingsScreen> createState() => _AdminSettingsScreenState();
}

class _AdminSettingsScreenState extends ConsumerState<AdminSettingsScreen> {
  final _siteNameCtrl = TextEditingController();
  final _descriptionCtrl = TextEditingController();
  final _contactEmailCtrl = TextEditingController();
  final _genPerDayCtrl = TextEditingController();
  final _maxPromptsCtrl = TextEditingController();
  final _openaiKeyCtrl = TextEditingController();
  final _anthropicKeyCtrl = TextEditingController();
  final _googleKeyCtrl = TextEditingController();
  final _deepseekKeyCtrl = TextEditingController();
  final _githubTokenCtrl = TextEditingController();
  bool _loading = true;
  bool _saving = false;
  bool _obscureKeys = true;

  @override
  void initState() {
    super.initState();
    _fetch();
  }

  @override
  void dispose() {
    _siteNameCtrl.dispose();
    _descriptionCtrl.dispose();
    _contactEmailCtrl.dispose();
    _genPerDayCtrl.dispose();
    _maxPromptsCtrl.dispose();
    _openaiKeyCtrl.dispose();
    _anthropicKeyCtrl.dispose();
    _googleKeyCtrl.dispose();
    _deepseekKeyCtrl.dispose();
    _githubTokenCtrl.dispose();
    super.dispose();
  }

  Future<void> _fetch() async {
    setState(() => _loading = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      final res = await dio.get(ApiConstants.adminSettings);
      final s = res.data as Map<String, dynamic>? ?? {};
      _siteNameCtrl.text = s['site_name'] ?? 'PromptCraft';
      _descriptionCtrl.text = s['site_description'] ?? '';
      _contactEmailCtrl.text = s['contact_email'] ?? '';
      _genPerDayCtrl.text = '${s['generations_per_day'] ?? 50}';
      _maxPromptsCtrl.text = '${s['max_prompts'] ?? 100}';
      final keys = s['api_keys'] as Map<String, dynamic>? ?? {};
      _openaiKeyCtrl.text = keys['openai'] ?? '';
      _anthropicKeyCtrl.text = keys['anthropic'] ?? '';
      _googleKeyCtrl.text = keys['google'] ?? '';
      _deepseekKeyCtrl.text = keys['deepseek'] ?? '';
      _githubTokenCtrl.text = keys['github'] ?? '';
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.put(ApiConstants.adminSettings, data: {
        'site_name': _siteNameCtrl.text,
        'site_description': _descriptionCtrl.text,
        'contact_email': _contactEmailCtrl.text,
        'generations_per_day': int.tryParse(_genPerDayCtrl.text) ?? 50,
        'max_prompts': int.tryParse(_maxPromptsCtrl.text) ?? 100,
        'api_keys': {
          'openai': _openaiKeyCtrl.text,
          'anthropic': _anthropicKeyCtrl.text,
          'google': _googleKeyCtrl.text,
          'deepseek': _deepseekKeyCtrl.text,
          'github': _githubTokenCtrl.text,
        },
      });
      if (mounted) Helpers.showToast('تم حفظ الإعدادات');
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'فشل الحفظ', isError: true);
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('الإعدادات')),
      drawer: const AdminDrawer(currentRoute: '/admin/settings'),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _buildSection('الإعدادات العامة', [
                    TextField(controller: _siteNameCtrl, decoration: const InputDecoration(labelText: 'اسم الموقع', prefixIcon: Icon(Icons.public))),
                    const SizedBox(height: 12),
                    TextField(controller: _descriptionCtrl, decoration: const InputDecoration(labelText: 'وصف الموقع', prefixIcon: Icon(Icons.description)), maxLines: 2),
                    const SizedBox(height: 12),
                    TextField(controller: _contactEmailCtrl, decoration: const InputDecoration(labelText: 'البريد الإلكتروني للتواصل', prefixIcon: Icon(Icons.email))),
                  ]),
                  const SizedBox(height: 16),
                  _buildSection('الحدود والإعدادات', [
                    TextField(controller: _genPerDayCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'عدد التوليدات المسموحة يومياً', prefixIcon: Icon(Icons.bolt))),
                    const SizedBox(height: 12),
                    TextField(controller: _maxPromptsCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'الحد الأقصى للبرومبتات لكل مستخدم', prefixIcon: Icon(Icons.auto_awesome))),
                  ]),
                  const SizedBox(height: 16),
                  _buildSection('مفاتيح API', [
                    _apiKeyField('OpenAI', _openaiKeyCtrl),
                    const SizedBox(height: 12),
                    _apiKeyField('Anthropic (Claude)', _anthropicKeyCtrl),
                    const SizedBox(height: 12),
                    _apiKeyField('Google (Gemini)', _googleKeyCtrl),
                    const SizedBox(height: 12),
                    _apiKeyField('DeepSeek', _deepseekKeyCtrl),
                    const SizedBox(height: 12),
                    _apiKeyField('GitHub Token', _githubTokenCtrl),
                  ]),
                  const SizedBox(height: 24),
                  FilledButton.icon(
                    onPressed: _saving ? null : _save,
                    icon: _saving ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.save),
                    label: Text(_saving ? 'جارٍ الحفظ...' : 'حفظ الإعدادات'),
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _apiKeyField(String label, TextEditingController ctrl) {
    return TextField(
      controller: ctrl,
      obscureText: _obscureKeys,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: const Icon(Icons.vpn_key),
        suffixIcon: IconButton(
          icon: Icon(_obscureKeys ? Icons.visibility_off : Icons.visibility),
          onPressed: () => setState(() => _obscureKeys = !_obscureKeys),
        ),
      ),
    );
  }
}
