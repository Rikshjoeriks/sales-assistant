# Logging Workflow

Use these log artifacts to preserve a complete audit trail after every confirmed implementation action.

1. Run the `/log-latest` command (or simply instruct the assistant to “log latest”).
2. Provide:
   - Prompt summary
   - Confirmation/clarification notes
   - Implementation summary and artifacts touched
   - Verification evidence (tests, lint, manual checks) with the exact command(s) executed (e.g., `poetry run pytest tests/unit/customers`)
   - Tooling/services changes
   - Structural changes (new files, renamed folders, etc.)
3. The assistant will update:
   - `docs/logs/task-journal.md`
   - `docs/reference/tooling-registry.md` (if tooling changed)
   - `docs/reference/project-map.md` (if structure changed)

No further work may begin until the log entry is captured. Keep entries chronological so we can trace the project narrative effortlessly.
