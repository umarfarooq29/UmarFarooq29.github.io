import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/task_item.dart';

class TaskApiService {
  TaskApiService({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  Future<List<TaskItem>> fetchSampleTasks() async {
    final uri = Uri.parse('https://jsonplaceholder.typicode.com/todos?_limit=8');
    final response = await _client.get(uri);

    if (response.statusCode != 200) {
      throw Exception('Unable to load task data');
    }

    final data = jsonDecode(response.body) as List<dynamic>;
    return data
        .map((item) => TaskItem.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}
