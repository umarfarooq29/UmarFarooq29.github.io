import 'package:flutter/material.dart';

class ResponsiveShell extends StatelessWidget {
  const ResponsiveShell({
    super.key,
    required this.compact,
    required this.wide,
  });

  final Widget compact;
  final Widget wide;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= 820) {
          return wide;
        }
        return compact;
      },
    );
  }
}
