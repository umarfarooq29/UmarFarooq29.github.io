import 'package:cloud_firestore/cloud_firestore.dart';

import '../models/task_item.dart';

class FirebaseTaskRepository {
  FirebaseTaskRepository({FirebaseFirestore? firestore})
      : _firestore = firestore ?? FirebaseFirestore.instance;

  final FirebaseFirestore _firestore;

  Stream<List<TaskItem>> watchTasks() {
    return _firestore.collection('tasks').snapshots().map((snapshot) {
      return snapshot.docs.map((doc) {
        final data = doc.data();
        return TaskItem(
          id: doc.id,
          title: data['title'] as String? ?? 'Untitled task',
          owner: data['owner'] as String? ?? 'Team',
          status: data['status'] as String? ?? 'Open',
          priority: data['priority'] as String? ?? 'Medium',
        );
      }).toList();
    });
  }

  Future<void> upsertTask(TaskItem task) {
    return _firestore.collection('tasks').doc(task.id).set(task.toMap());
  }
}
