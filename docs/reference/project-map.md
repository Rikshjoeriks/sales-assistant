# Project Knowledge Map

Track every directory and key file so collaborators (and the assistant) can navigate with certainty. Update this map whenever structure changes.

| Path | Type | Purpose / Key Contents | Owner / Notes |
|------|------|------------------------|---------------|
| `/` | Directory | Repository root holding governance, specs, and docs. |  |
| `/.gitignore` | File | Git ignore rules. |  |
| `/.specify/` | Directory | Spec Kit configuration, memory, and helper scripts. | Governed by constitution updates. |
| `/.specify/memory/constitution.md` | File | Canonical governance document (v1.6.0). | Update via controlled amendments only. |
| `/.specify/scripts/` | Directory | Automation scripts (e.g., plan setup). | Leave untouched unless updating Spec Kit tooling. |
| `/.specify/templates/` | Directory | Template files used by Spec Kit. | Reference only. |
| `/docs/` | Directory | Documentation hub (logs, manuals, reference). |  |
| `/docs/logs/` | Directory | Task journal, logging README, future decision logs. | Update per `/log-latest`. |
| `/docs/logs/task-journal.md` | File | Chronological task and prompt log with verification evidence. | Append after every implementation action. |
| `/docs/logs/README.md` | File | Instructions for logging workflow. | Keep aligned with constitution. |
| `/docs/manual/` | Directory | Process manuals and onboarding guides. |  |
| `/docs/manual/working-with-spec-kit.md` | File | Project playbook and handshake protocol. | Update as workflow evolves. |
| `/docs/reference/` | Directory | Knowledge map, tooling registry, future reference docs. |  |
| `/docs/reference/project-map.md` | File | This file—structural map. | Maintain diligently. |
| `/docs/reference/tooling-registry.md` | File | Agreed instruments, plugins, services with versions and risks. | Update whenever tooling changes. |
| `/specs/` | Directory | Feature specifications and planning artifacts. |  |
| `/specs/main/` | Directory | Core sales assistant specification package. | Houses spec, plan, tasks, research. |
| `/specs/main/spec.md` | File | Functional spec for knowledge ingestion & content generation. | Update when scope changes. |
| `/specs/main/plan.md` | File | Implementation roadmap with progress tracking. | Mark phases as complete. |
| `/specs/main/tasks.md` | File | Master task list (T001–T084). | Reference for task IDs. |
| `/specs/main/research.md` | File | Supporting research notes. | Extend as new insights land. |
| `/specs/main/data-model.md` | File | Entities and schema overview. | Sync with code changes once implemented. |
| `/specs/main/contracts/` | Directory | API contracts (knowledge, customers, recommendations). | Keep in lockstep with service evolution. |
| `/specs/main/quickstart.md` | File | Setup/run instructions once implemented. | Update when environment shifts. |
| `/README.md` | File | Repo overview. | Refresh when major milestones achieved. |
| `/MyProject/` | Directory | Legacy or placeholder content (investigate before use). | Flag for cleanup in future. |
| `/Staying_organized_and_productive.md` | File | Legacy note—review for relevance. | Consider migrating or archiving. |
| `/steps1.md` | File | Legacy instructions. | Evaluate during implementation phase. |

> **Reminder:** Whenever you add, move, or remove files/directories, update this table in the same commit. Include the reason or task ID in the notes column.
