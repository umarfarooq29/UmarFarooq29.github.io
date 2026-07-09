import 'package:flutter/material.dart';

import '../models/task_item.dart';
import '../services/task_api_service.dart';
import '../widgets/responsive_shell.dart';

class TaskDashboardScreen extends StatefulWidget {
  const TaskDashboardScreen({super.key});

  @override
  State<TaskDashboardScreen> createState() => _TaskDashboardScreenState();
}

class _TaskDashboardScreenState extends State<TaskDashboardScreen> {
  final TaskApiService _apiService = TaskApiService();
  late Future<List<TaskItem>> _tasksFuture;

  @override
  void initState() {
    super.initState();
    _tasksFuture = _apiService.fetchSampleTasks();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('TaskFlow'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: () {
              setState(() {
                _tasksFuture = _apiService.fetchSampleTasks();
              });
            },
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: FutureBuilder<List<TaskItem>>(
        future: _tasksFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(
              child: Text('Could not load tasks: ${snapshot.error}'),
            );
          }

          final tasks = snapshot.data ?? const <TaskItem>[];
          return ResponsiveShell(
            compact: _CompactTaskLayout(tasks: tasks),
            wide: _WideTaskLayout(tasks: tasks),
          );
        },
      ),
    );
  }
}

class _CompactTaskLayout extends StatelessWidget {
  const _CompactTaskLayout({required this.tasks});

  final List<TaskItem> tasks;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemBuilder: (context, index) => _TaskTile(task: tasks[index]),
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemCount: tasks.length,
    );
  }
}

class _WideTaskLayout extends StatelessWidget {
  const _WideTaskLayout({required this.tasks});

  final List<TaskItem> tasks;

  @override
  Widget build(BuildContext context) {
    final done = tasks.where((task) => task.status == 'Done').length;
    final open = tasks.length - done;

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 280,
            child: Column(
              children: [
                _MetricCard(label: 'Open', value: open.toString(), icon: Icons.pending_actions),
                const SizedBox(height: 16),
                _MetricCard(label: 'Done', value: done.toString(), icon: Icons.task_alt),
              ],
            ),
          ),
          const SizedBox(width: 24),
          Expanded(
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                maxCrossAxisExtent: 340,
                mainAxisExtent: 150,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
              ),
              itemBuilder: (context, index) => _TaskTile(task: tasks[index]),
              itemCount: tasks.length,
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  const _MetricCard({
    required this.label,
    required this.value,
    required this.icon,
  });

  final String label;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Icon(icon, size: 32),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: Theme.of(context).textTheme.labelLarge),
                Text(value, style: Theme.of(context).textTheme.headlineMedium),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _TaskTile extends StatelessWidget {
  const _TaskTile({required this.task});

  final TaskItem task;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    task.title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                Chip(label: Text(task.status)),
              ],
            ),
            const Spacer(),
            Row(
              children: [
                const Icon(Icons.person_outline, size: 18),
                const SizedBox(width: 6),
                Text(task.owner),
                const Spacer(),
                Text(task.priority),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
