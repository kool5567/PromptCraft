import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';

import '../../../../core/constants/api_constants.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/utils/helpers.dart';
import '../widgets/admin_drawer.dart';

class AdminImportsScreen extends ConsumerStatefulWidget {
  const AdminImportsScreen({super.key});

  @override
  ConsumerState<AdminImportsScreen> createState() => _AdminImportsScreenState();
}

class _AdminImportsScreenState extends ConsumerState<AdminImportsScreen> {
  final _repoCtrl = TextEditingController();
  final _branchCtrl = TextEditingController(text: 'main');
  final _patternCtrl = TextEditingController(text: '*.md');
  List<Map<String, dynamic>> _jobs = [];
  bool _loading = true;
  bool _importing = false;
  bool _uploading = false;

  @override
  void initState() {
    super.initState();
    _fetchJobs();
  }

  @override
  void dispose() {
    _repoCtrl.dispose();
    _branchCtrl.dispose();
    _patternCtrl.dispose();
    super.dispose();
  }

  Future<void> _fetchJobs() async {
    setState(() => _loading = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      final res = await dio.get(ApiConstants.importJobs);
      setState(() {
        _jobs = (res.data is List ? res.data : res.data['jobs'] ?? []).cast<Map<String, dynamic>>();
      });
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _importGithub() async {
    if (_repoCtrl.text.trim().isEmpty) {
      Helpers.showToast('الرجاء إدخال رابط المستودع', isError: true);
      return;
    }
    setState(() => _importing = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      await dio.post(ApiConstants.importGithub, data: {
        'repo_url': _repoCtrl.text.trim(),
        'branch': _branchCtrl.text.trim(),
        'pattern': _patternCtrl.text.trim(),
      });
      if (mounted) Helpers.showToast('تم بدء الاستيراد');
      _repoCtrl.clear();
      _fetchJobs();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'فشل الاستيراد', isError: true);
    } finally {
      if (mounted) setState(() => _importing = false);
    }
  }

  Future<void> _importFile() async {
    final pathCtrl = TextEditingController();
    final picked = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('استيراد من ملف'),
        content: TextField(
          controller: pathCtrl,
          decoration: const InputDecoration(
            labelText: 'مسار الملف',
            hintText: 'C:\\path\\to\\file.json',
            prefixIcon: Icon(Icons.file_present),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('إلغاء')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('رفع')),
        ],
      ),
    );
    if (picked != true || pathCtrl.text.trim().isEmpty) return;
    final filePath = pathCtrl.text.trim();
    if (!File(filePath).existsSync()) {
      Helpers.showToast('الملف غير موجود', isError: true);
      return;
    }
    setState(() => _uploading = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath, filename: filePath.split('\\').last.split('/').last),
      });
      await dio.post(ApiConstants.importFile, data: formData);
      if (mounted) Helpers.showToast('تم رفع الملف وبدء الاستيراد');
      _fetchJobs();
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'فشل الرفع', isError: true);
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('الاستيراد')),
      drawer: const AdminDrawer(currentRoute: '/admin/imports'),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildGithubCard(),
            const SizedBox(height: 16),
            _buildFileUploadCard(),
            const SizedBox(height: 24),
            Text('سجل الاستيراد', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            _buildJobList(),
          ],
        ),
      ),
    );
  }

  Widget _buildGithubCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.link, color: AppColors.primary),
                const SizedBox(width: 8),
                Text('استيراد من GitHub', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _repoCtrl,
              decoration: const InputDecoration(labelText: 'رابط المستودع', hintText: 'https://github.com/owner/repo', prefixIcon: Icon(Icons.code)),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(controller: _branchCtrl, decoration: const InputDecoration(labelText: 'الفرع', prefixIcon: Icon(Icons.call_split))),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(controller: _patternCtrl, decoration: const InputDecoration(labelText: 'نوع الملفات', prefixIcon: Icon(Icons.pattern))),
                ),
              ],
            ),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: _importing ? null : _importGithub,
              icon: _importing ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.download),
              label: Text(_importing ? 'جارٍ الاستيراد...' : 'بدء الاستيراد'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFileUploadCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.upload_file, color: AppColors.secondary),
                const SizedBox(width: 8),
                Text('استيراد من ملف', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: _uploading ? null : _importFile,
              icon: _uploading ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.upload),
              label: Text(_uploading ? 'جارٍ الرفع...' : 'رفع ملف JSON أو CSV'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildJobList() {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_jobs.isEmpty) return const Card(child: Padding(padding: EdgeInsets.all(24), child: Center(child: Text('لا توجد عمليات استيراد سابقة'))));
    return Column(
      children: _jobs.map((j) {
        final status = j['status'] ?? 'pending';
        final statusInfo = _jobStatusInfo(status);
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(color: statusInfo.color.withOpacity(0.12), borderRadius: BorderRadius.circular(8)),
              child: Icon(statusInfo.icon, color: statusInfo.color, size: 20),
            ),
            title: Text(j['source'] ?? j['repo_url'] ?? j['filename'] ?? 'غير معروف', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14), maxLines: 1, overflow: TextOverflow.ellipsis),
            subtitle: Text('${j['imported_count'] ?? 0} برومبت • ${_dateLabel(j['created_at'])}', style: const TextStyle(fontSize: 12)),
            trailing: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(color: statusInfo.color.withOpacity(0.12), borderRadius: BorderRadius.circular(8)),
              child: Text(statusInfo.label, style: TextStyle(color: statusInfo.color, fontSize: 11, fontWeight: FontWeight.w600)),
            ),
          ),
        );
      }).toList(),
    );
  }

  _JobStatusInfo _jobStatusInfo(String status) {
    switch (status) {
      case 'completed': return _JobStatusInfo(Icons.check_circle, AppColors.secondary, 'مكتمل');
      case 'processing': return _JobStatusInfo(Icons.sync, AppColors.primary, 'قيد المعالجة');
      case 'failed': return _JobStatusInfo(Icons.error, AppColors.error, 'فشل');
      default: return _JobStatusInfo(Icons.schedule, AppColors.gold, 'معلق');
    }
  }

  String _dateLabel(String? raw) {
    if (raw == null) return '';
    final dt = DateTime.tryParse(raw);
    return dt != null ? Helpers.timeAgo(dt) : '';
  }
}

class _JobStatusInfo {
  final IconData icon;
  final Color color;
  final String label;
  _JobStatusInfo(this.icon, this.color, this.label);
}
