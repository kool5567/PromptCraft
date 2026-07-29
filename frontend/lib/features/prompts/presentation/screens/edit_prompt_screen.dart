import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/network/dio_client.dart';
import '../../../data/datasources/api_service.dart';
import '../../../data/repositories/prompt_repository.dart';
import '../../../domain/entities/prompt_model.dart';
import '../../../core/utils/helpers.dart';
import 'create_prompt_screen.dart';

class EditPromptScreen extends ConsumerStatefulWidget {
  final String promptId;
  const EditPromptScreen({super.key, required this.promptId});

  @override
  ConsumerState<EditPromptScreen> createState() => _EditPromptScreenState();
}

class _EditPromptScreenState extends ConsumerState<EditPromptScreen> {
  PromptModel? _prompt;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadPrompt();
  }

  Future<void> _loadPrompt() async {
    try {
      final repo = ref.read(promptRepositoryProvider);
      final prompt = await repo.getPrompt(widget.promptId);
      if (mounted) setState(() { _prompt = prompt; _loading = false; });
    } catch (e) {
      if (mounted) {
        Helpers.showToast('فشل تحميل البرومبت', isError: true);
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (_prompt == null) return const Scaffold(body: Center(child: Text('البرومبت غير موجود')));

    return CreatePromptScreen(editPrompt: _prompt);
  }
}
