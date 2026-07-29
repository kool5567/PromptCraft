import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class LibraryScreen extends ConsumerWidget {
  const LibraryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('المكتبة العامة')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          Text('المكتبة العامة - قريباً', style: TextStyle(fontSize: 18)),
        ],
      ),
    );
  }
}
