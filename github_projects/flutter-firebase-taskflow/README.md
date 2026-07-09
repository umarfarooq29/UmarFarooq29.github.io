# TaskFlow Flutter Firebase App

Portfolio project for Flutter Development skills: Flutter, Dart, Firebase, REST APIs, Responsive UI, and Git.

## Project Goal

Create a clean task management app foundation that syncs tasks through Firebase and can also read external tasks from a REST API.

## What This Project Shows

| Skill | Evidence in this repo |
| --- | --- |
| Flutter | Full `lib/` app structure with Material 3 widgets. |
| Dart | Models, services, and screen code are written in Dart. |
| Firebase | `firebase_core`, `firebase_auth`, and `cloud_firestore` are included. |
| REST APIs | `TaskApiService` loads sample tasks from JSONPlaceholder. |
| Responsive UI | LayoutBuilder switches between compact and wide layouts. |
| Git | `.gitignore` and GitHub publishing notes are included. |

## Run

```bash
flutter pub get
flutterfire configure
flutter run
```

Firebase setup is intentionally not committed with private project values. Run `flutterfire configure` to generate `firebase_options.dart` for your own Firebase project.

## Project Structure

```text
lib/
  main.dart
  models/task_item.dart
  screens/task_dashboard_screen.dart
  services/firebase_task_repository.dart
  services/task_api_service.dart
  widgets/responsive_shell.dart
```

## Portfolio Summary

This project demonstrates a real Flutter app architecture with Firebase sync, REST API integration, responsive layout, and GitHub-ready structure.
