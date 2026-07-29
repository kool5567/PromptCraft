import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_theme.dart';

class SubscriptionScreen extends ConsumerStatefulWidget {
  const SubscriptionScreen({super.key});

  @override
  ConsumerState<SubscriptionScreen> createState() => _SubscriptionScreenState();
}

class _SubscriptionScreenState extends ConsumerState<SubscriptionScreen> {
  int _selectedPlan = 1;

  final _plans = [
    {'name': 'Basic', 'price': '\$9.99', 'period': '/شهر', 'color': Colors.blue, 'features': ['50 توليد/يوم', '500 برومبت', 'قوالب كاملة', 'استيراد GitHub']},
    {'name': 'Pro', 'price': '\$19.99', 'period': '/شهر', 'color': AppTheme.primaryColor, 'features': ['غير محدود', 'برومبتات غير محدودة', 'برومبتات مميزة', 'API Access', 'دعم أولوية']},
    {'name': 'Enterprise', 'price': '\$49.99', 'period': '/شهر', 'color': AppTheme.accentColor, 'features': ['كل شي في Pro', '+10 حسابات فريق', 'علامة تجارية مخصصة', 'دعم 24/7']},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('الباقات والاشتراكات')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Text('اختر الباقة المناسبة', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('طوّر إنتاجيتك مع الباقات المميزة', style: TextStyle(color: Colors.grey.shade600)),
            const SizedBox(height: 24),
            ...List.generate(_plans.length, (i) => _buildPlanCard(i)),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {},
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 56),
                ),
                child: Text('اشترك الآن - ${_plans[_selectedPlan]['price']}${_plans[_selectedPlan]['period']}'),
              ),
            ),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () {},
              child: const Text('مقارنة الباقات'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPlanCard(int index) {
    final plan = _plans[index];
    final isSelected = _selectedPlan == index;
    final isPopular = index == 1;

    return GestureDetector(
      onTap: () => setState(() => _selectedPlan = index),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? plan['color'] as Color : Colors.grey.shade300,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Stack(
          children: [
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(plan['name'] as String, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                      Text('${plan['price']}${plan['period']}', style: TextStyle(color: plan['color'] as Color, fontSize: 24, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  ...(plan['features'] as List<String>).map((f) => Padding(
                    padding: const EdgeInsets.only(bottom: 6),
                    child: Row(
                      children: [
                        Icon(Icons.check_circle, size: 18, color: AppTheme.successColor),
                        const SizedBox(width: 8),
                        Text(f),
                      ],
                    ),
                  )),
                ],
              ),
            ),
            if (isPopular)
              Positioned(
                top: 12,
                right: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppTheme.accentColor,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text('الأكثر طلباً', style: TextStyle(color: Colors.white, fontSize: 10)),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
