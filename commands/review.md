---
description: Review a tool whose output a firm has to stand behind — execute it, document it, hunt its defects, write the checklist and the code review, then fact-check both.
argument-hint: "[path-to-tool] [--mode document|review|verify]"
---

Invoke the `review-the-tool` skill for the target below.

Target: $1
Mode: $2 (omit to let the skill infer it from the request)

If no target is given, ask for one before starting — do not review the current
working directory by assumption, because staging the wrong tree wastes an hour
of execution.
