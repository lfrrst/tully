---
description: Review a tool whose output a firm has to stand behind — execute it, document it, hunt its defects, write the checklist and the code review, then fact-check both.
argument-hint: "[path-to-tool] [--mode document|review|verify]"
---

Invoke the `review-the-tool` skill for the target below.

Arguments as given: $ARGUMENTS

Read them like this. The first bare word is the target — the tool to review. If
`--mode` appears, the word after it is the mode, one of `document`, `review` or
`verify`. Either may be absent.

With no target, ask for one before starting. Do not review the working directory
by assumption: staging the wrong tree wastes an hour of execution before anything
reveals the mistake.

With no mode, do not default — infer it from what the caller actually asked for,
by the rule in the skill, and say which mode you inferred before you begin.
