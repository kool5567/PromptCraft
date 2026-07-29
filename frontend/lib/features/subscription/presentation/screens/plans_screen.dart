import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/helpers.dart';
import '../../../data/datasources/api_service.dart';

final plansProvider = FutureProvider((ref) async {
  final api = ApiService(ref.read(dioClientProvider));
  return await api.getList(ApiConstants.subscriptionPlans);
});

class PlansScreen extends ConsumerStatefulWidget {
  const PlansScreen({super.key});

  @override
  ConsumerState<PlansScreen> createState() => _PlansScreenState();
}

class _PlansScreenState extends ConsumerState<PlansScreen> {
  String? _selectedPlan;
  bool _yearly = false;
  bool _loading = false;

  @override
  Widget build(BuildContext context) {
    final plans = ref.watch(plansProvider);
    final colors = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('خطط الاشتراك')),
      body: plans.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('$e')),
        data: (data) => SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Text('اختر خطتك المثالية', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: colors.onSurface)),
              const SizedBox(height: 8),
              Text('استمتع بميزات غير محدودة مع خططنا المميزة', style: TextStyle(color: colors.onSurface.withValues(alpha: 0.6))),
              const SizedBox(height: 20),
              SegmentedButton<bool>(
                segments: const [
                  ButtonSegment(value: false, label: Text('شهري')),
                  ButtonSegment(value: true, label: Text('سنوي')),
                ],
                selected: {_yearly},
                onSelectionChanged: (v) => setState(() => _yearly = v.first),
              ),
              const SizedBox(height: 24),
              ...(_buildPlanCards(context, colors, data.data ?? [])),
            ],
          ),
        ),
      ),
    );
  }

  List<Widget> _buildPlanCards(BuildContext context, ColorScheme colors, List<dynamic> plans) {
    if (plans.isEmpty) {
      plans = [
        {'id': 'basic', 'name': 'Basic', 'price': 9.99, 'features': ['50 توليد/يوم', '500 برومبت', 'قوالب كاملة', 'استيراد GitHub'], 'is_popular': false},
        {'id': 'pro', 'name': 'Pro', 'price': 19.99, 'features': ['توليد غير محدود', 'برومبتات غير محدودة', 'برومبتات مميزة', 'API access', 'دعم أولوي'], 'is_popular': true},
        {'id': 'enterprise', 'name': 'Enterprise', 'price': 49.99, 'features': ['كل ميزات Pro', 'فريق حتى 10+', 'علامة تجارية مخصصة', 'دعم 24/7'], 'is_popular': false},
      ];
    }
    return plans.map((plan) {
      final id = plan['id'] ?? '';
      final name = plan['name'] ?? '';
      final price = (plan['price'] ?? 9.99).toDouble();
      final features = (plan['features'] as List?)?.cast<String>() ?? [];
      final isPopular = plan['is_popular'] ?? false;
      final isSelected = _selectedPlan == id;

      return Padding(
        padding: const EdgeInsets.only(bottom: 16),
        child: GestureDetector(
          onTap: () => setState(() => _selectedPlan = id),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: isSelected ? colors.primary : colors.outline, width: isSelected ? 2 : 1),
              color: isSelected ? colors.primary.withValues(alpha: 0.05) : colors.surface,
            ),
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(name, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: colors.onSurface)),
                    const Spacer(),
                    if (isPopular)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                        decoration: BoxDecoration(color: colors.primary, borderRadius: BorderRadius.circular(20)),
                        child: const Text('الأكثر طلباً', style: TextStyle(color: Colors.white, fontSize: 12)),
                      ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text('\$${_yearly ? (price * 10).toStringAsFixed(0) : price.toStringAsFixed(2)}',
                      style: TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: colors.onSurface)),
                    Text('/${_yearly ? 'السنة' : 'الشهر'}', style: TextStyle(color: colors.onSurface.withValues(alpha: 0.5))),
                  ],
                ),
                const SizedBox(height: 16),
                ...features.map((f) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    children: [
                      Icon(Icons.check_circle, size: 20, color: colors.secondary),
                      const SizedBox(width: 8),
                      Text(f, style: TextStyle(color: colors.onSurface.withValues(alpha: 0.8))),
                    ],
                  ),
                )),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton(
                    onPressed: _loading ? null : () => _subscribe(id),
                    style: isPopular ? null : FilledButton.styleFrom(backgroundColor: colors.surfaceContainerHighest, foregroundColor: colors.onSurface),
                    child: _loading ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)) : Text(isSelected ? 'اشترك الآن' : 'اختر هذه الخطة'),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }).toList();
  }

  Future<void> _subscribe(String planId) async {
    setState(() => _loading = true);
    try {
      final api = ApiService(ref.read(dioClientProvider));
      await api.post(ApiConstants.subscriptionSubscribe, data: {'plan_type': planId, 'payment_provider': 'stripe'});
      Helpers.showToast('تم الاشتراك بنجاح');
      if (mounted) context.pop();
    } catch (e) {
      Helpers.showToast('فشل الاشتراك: $e', isError: true);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }
}
