import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class PromptDetailScreen extends ConsumerWidget {
  final String id;
  const PromptDetailScreen({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('تفاصيل البرومبت')),
      body: Center(child: Text('البرومبت: $id')),
    );
  }
}
