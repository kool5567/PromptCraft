import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';

import '../../../../core/constants/api_constants.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/utils/helpers.dart';
import '../widgets/admin_drawer.dart';

class AdminAnalyticsScreen extends ConsumerStatefulWidget {
  const AdminAnalyticsScreen({super.key});

  @override
  ConsumerState<AdminAnalyticsScreen> createState() => _AdminAnalyticsScreenState();
}

class _AdminAnalyticsScreenState extends ConsumerState<AdminAnalyticsScreen> {
  Map<String, dynamic>? _data;
  bool _loading = true;
  DateTimeRange? _dateRange;

  @override
  void initState() {
    super.initState();
    final now = DateTime.now();
    _dateRange = DateTimeRange(start: now.subtract(const Duration(days: 30)), end: now);
    _fetch();
  }

  Future<void> _fetch() async {
    setState(() => _loading = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      final params = <String, dynamic>{};
      if (_dateRange != null) {
        params['start_date'] = _dateRange!.start.toIso8601String().split('T')[0];
        params['end_date'] = _dateRange!.end.toIso8601String().split('T')[0];
      }
      final res = await dio.get(ApiConstants.adminAnalytics, queryParameters: params);
      setState(() => _data = res.data);
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'حدث خطأ', isError: true);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _pickDateRange() async {
    final picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2024),
      lastDate: DateTime.now(),
      initialDateRange: _dateRange,
      locale: const Locale('ar'),
    );
    if (picked != null) {
      setState(() => _dateRange = picked);
      _fetch();
    }
  }

  void _exportCsv() async {
    try {
      final dio = ref.read(dioClientProvider).dio;
      final res = await dio.get('${ApiConstants.adminAnalytics}/export',
        queryParameters: {
          if (_dateRange != null) 'start_date': _dateRange!.start.toIso8601String().split('T')[0],
          if (_dateRange != null) 'end_date': _dateRange!.end.toIso8601String().split('T')[0],
        },
      );
      final csv = res.data is String ? res.data : const JsonEncoder.withIndent('  ').convert(res.data);
      if (mounted) Helpers.showToast('تم التصدير بنجاح');
    } on DioException catch (e) {
      if (mounted) Helpers.showToast(e.message ?? 'فشل التصدير', isError: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('السجلات والإحصائيات')),
      drawer: const AdminDrawer(currentRoute: '/admin/analytics'),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _fetch,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildDateRangeRow(),
                    const SizedBox(height: 20),
                    _buildUserGrowthChart(),
                    const SizedBox(height: 20),
                    _buildGenerationChart(),
                    const SizedBox(height: 20),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(child: _buildTopPrompts()),
                        const SizedBox(width: 12),
                        Expanded(child: _buildCategoryDistribution()),
                      ],
                    ),
                    const SizedBox(height: 20),
                    _buildExportButton(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildDateRangeRow() {
    final start = _dateRange?.start;
    final end = _dateRange?.end;
    return Row(
      children: [
        const Icon(Icons.date_range, color: AppColors.primary),
        const SizedBox(width: 8),
        Text(
          '${start?.day ?? 1}/${start?.month ?? 1}/${start?.year ?? 2024} - ${end?.day ?? 1}/${end?.month ?? 1}/${end?.year ?? 2024}',
          style: const TextStyle(fontWeight: FontWeight.w500),
        ),
        const Spacer(),
        TextButton.icon(
          onPressed: _pickDateRange,
          icon: const Icon(Icons.edit_calendar, size: 18),
          label: const Text('تغيير'),
        ),
      ],
    );
  }

  Widget _buildUserGrowthChart() {
    final points = (_data?['user_growth'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('نمو المستخدمين', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 16),
            if (points.isEmpty)
              const Center(child: Text('لا توجد بيانات'))
            else
              SizedBox(
                height: 160,
                child: _buildBarChart(points, 'count', AppColors.primary),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildGenerationChart() {
    final points = (_data?['generations'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('عدد التوليدات', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 16),
            if (points.isEmpty)
              const Center(child: Text('لا توجد بيانات'))
            else
              SizedBox(
                height: 160,
                child: _buildBarChart(points, 'count', AppColors.secondary),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildBarChart(List<Map<String, dynamic>> points, String valueKey, Color color) {
    if (points.isEmpty) return const SizedBox.shrink();
    final maxVal = points.fold<double>(0, (m, p) => (p[valueKey] ?? 0).toDouble() > m ? (p[valueKey] ?? 0).toDouble() : m);
    if (maxVal == 0) return const Center(child: Text('لا توجد قيم'));
    return LayoutBuilder(
      builder: (_, constraints) => Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: points.map((p) {
          final val = (p[valueKey] ?? 0).toDouble();
          final height = (val / maxVal) * constraints.maxHeight * 0.85;
          final label = p['date'] ?? p['label'] ?? '';
          final shortLabel = label.toString().length > 5 ? label.toString().substring(label.toString().length - 5) : label.toString();
          return Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 2),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  if (val > 0)
                    Text('${val.toInt()}', style: TextStyle(fontSize: 9, color: Colors.grey.shade600)),
                  const SizedBox(height: 2),
                  Container(
                    height: height.clamp(4, constraints.maxHeight * 0.85),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.7),
                      borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(shortLabel, style: TextStyle(fontSize: 8, color: Colors.grey.shade600), textAlign: TextAlign.center),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildTopPrompts() {
    final top = (_data?['top_prompts'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('أفضل البرومبتات', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 12),
            if (top.isEmpty)
              const Padding(padding: EdgeInsets.all(8), child: Text('لا توجد بيانات'))
            else
              ...top.take(5).map((p) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(color: AppColors.gold.withOpacity(0.12), borderRadius: BorderRadius.circular(6)),
                      child: const Icon(Icons.auto_awesome, size: 16, color: AppColors.gold),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(p['title'] ?? '', style: const TextStyle(fontSize: 13), maxLines: 1, overflow: TextOverflow.ellipsis),
                    ),
                    Text('${p['usage_count'] ?? 0}', style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                  ],
                ),
              )),
          ],
        ),
      ),
    );
  }

  Widget _buildCategoryDistribution() {
    final dist = (_data?['category_distribution'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('توزيع التصنيفات', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 12),
            if (dist.isEmpty)
              const Padding(padding: EdgeInsets.all(8), child: Text('لا توجد بيانات'))
            else
              ...dist.take(6).map((c) {
                final count = (c['count'] ?? 0).toDouble();
                final total = dist.fold<double>(0, (s, d) => s + (d['count'] ?? 0).toDouble());
                final pct = total > 0 ? count / total : 0.0;
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(c['name'] ?? '', style: const TextStyle(fontSize: 13)),
                          const Spacer(),
                          Text('${count.toInt()} (${(pct * 100).toStringAsFixed(0)}%)', style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
                        ],
                      ),
                      const SizedBox(height: 4),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: pct,
                          backgroundColor: AppColors.primary.withOpacity(0.1),
                          color: AppColors.primary,
                          minHeight: 6,
                        ),
                      ),
                    ],
                  ),
                );
              }),
          ],
        ),
      ),
    );
  }

  Widget _buildExportButton() {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        onPressed: _exportCsv,
        icon: const Icon(Icons.download),
        label: const Text('تصدير CSV'),
      ),
    );
  }
}
