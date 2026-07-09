class TaskItem {
  const TaskItem({
    required this.id,
    required this.title,
    required this.owner,
    required this.status,
    required this.priority,
  });

  final String id;
  final String title;
  final String owner;
  final String status;
  final String priority;

  factory TaskItem.fromJson(Map<String, dynamic> json) {
    return TaskItem(
      id: json['id'].toString(),
      title: json['title'] as String? ?? 'Untitled task',
      owner: json['owner'] as String? ?? 'Team',
      status: json['completed'] == true ? 'Done' : (json['status'] as String? ?? 'Open'),
      priority: json['priority'] as String? ?? 'Medium',
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'owner': owner,
      'status': status,
      'priority': priority,
    };
  }
}
