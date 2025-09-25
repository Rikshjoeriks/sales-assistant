# Working With Spec Kit: Sales Assistant Project Playbook

Welcome aboard! This guide keeps our Domain-Specific Retrieval-Augmented AI Copilot project clean, precise, and productive. Read it front-to-back once, then keep it handy while you build.

---

## 1. Core Workflow at a Glance

1. **Clarify → Spec → Plan → Tasks → Build → Validate**
   - `/clarify` (or manual clarifications) to confirm requirements.
   - `specs/main/spec.md` describes feature scope.
   - `/plan` (or our manual plan) produces `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`.
   - `/tasks` (we generated manually) lives at `specs/main/tasks.md`.
   - Execute tasks in order, keeping tests first (TDD).
   - Run validation (tests, lint, quickstart steps) before declaring a feature done.

2. **One feature = one cycle**
   - Stay focused on sales assistant functionality until the loop is complete.
   - Add new features by repeating the cycle in a new `specs/<feature-name>/` directory.

3. **Git rhythm**
   - Commit at logical milestones (e.g., “tests for knowledge API”, “implement knowledge ingestion service”).
   - Push once a small vertical slice is working and passing tests.

---

## 2. Feeding Me Information (Best Practices)

1. **Use structured prompts**
   - Tell me the file path, the specific task number (from `tasks.md`), and the desired outcome.
   - Example: “I’m working on T026 in `src/app/knowledge/services/ingestion_service.py`. Here’s the current code… Please implement PDF/TXT/DOCX parsing.”

2. **Reference artifacts**
   - Point me to relevant sections in `plan.md`, `research.md`, or `contracts/` so I stay aligned with architecture decisions.
   - Copy critical snippets if they’re short; otherwise say “see plan.md → Phase 3.3 requirements”.
   - Confirm tooling choices up front: reference `docs/reference/tooling-registry.md` or propose additions before we start coding so we stay aligned with approved instruments.

3. **Flag open questions**
   - If something is unclear (e.g., missing spec details), ask for clarification *before* coding.
   - Document decisions inline (comments) or in `docs/notes/` if they affect future work.

4. **Keep context tight**
   - Avoid pasting entire large files unless necessary; target the snippet you want changed plus a bit of context (3-5 lines around it).
   - Mention assumptions explicitly so we can verify them against the constitution.
   - After we finish an implementation response, expect the assistant to trigger `/log-latest` automatically to capture the prompt, response summary, artifacts touched, verification evidence, tooling updates, and structural changes.

### Command Processing Protocol (Constitution Requirement)
Every time you give a command or suggestion, we MUST follow this four-step workflow:
1. **Classify** – State whether you need a clarification, spec update, plan change, task adjustment, or implementation action.
2. **Check prerequisites** – Confirm the required artifacts exist (e.g., spec before plan, plan before tasks). If something is missing, pause and create it first.
3. **Document** – Log the decision in the appropriate file (`spec.md`, `plan.md`, `tasks.md`, or `docs/notes/decision-log.md`) before coding.
4. **Execute & report** – Perform the agreed work, then summarize what changed and list next steps.

**Prompt/Response Handshake**
- You issue a request with the classification upfront (e.g., “Task Update: Please implement T026…”).
- I reflect it back, confirm understanding, highlight any missing prerequisites, and point out if running a spec-kit command (clarify/plan/tasks) would help.
- I wait for your go-ahead before executing substantive work.
- After execution, I report results plus any follow-up questions or recommended next commands.
- Immediately after reporting results, I run `/log-latest` to persist the transcript details and note tooling or structural changes. You’ll see the journal/tooling/map updates in the same turn.

---

## 3. Project Hygiene Checklist

### Daily
- Pull the latest main branch.
- Review `specs/main/tasks.md` and choose the next task.
- Run `make lint` / `make test` (once those commands exist) before committing.

### Per Task
1. Read the related spec/plan section.
2. Confirm or update tooling decisions in the registry (if the task introduces new instruments/plugins/interfaces) and note task ownership in the journal before coding.
3. Write/update tests first (they must fail).
4. Implement code to make tests pass.
5. Capture verification evidence: list the commands run (tests, lint, manual scripts), record outcomes in the task journal’s Verification Evidence column, and block completion if anything fails.
6. Add or update docs if behavior changes.
7. Run `/log-latest` so the assistant records the prompt, response, verification evidence, tooling updates, and structural changes before moving on.
8. Commit with descriptive message (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).

### Tooling Alignment & Conflict Prevention Playbook

- **Registry first**: Every time you add or change a tool, external API, plugin, or interface layer, add an entry to `docs/reference/tooling-registry.md` with configuration and risk notes. Don’t start implementation until the entry exists.
- **Single-task focus**: Claim the task in the journal before touching code, and avoid parallel work on overlapping files unless pairing live.
- **Branch hygiene**: Create a dedicated branch per task, rebase/pull from `main` at the start of each session, and re-run tests after syncing.
- **Early integration tests**: When a new tool enters the stack, add a smoke test or script immediately so conflicts surface before downstream tasks depend on it.
- **Pair reviews**: For high-risk integrations, request a synchronous walkthrough of the plan before coding and again before merging.
- **Feature flags & toggles**: Introduce feature flags when deploying partially complete flows to keep the main branch releasable.

### `/log-latest` Command Cheat Sheet

Use this custom command (or tell the assistant “log latest”) after every implementation step:

1. **Trigger** – Assistant prompts itself to gather: prompt summary, confirmation/clarification notes, implementation summary, artifacts touched, verification evidence, tooling deltas, structural deltas, and next steps.
2. **Task Journal Update** – Append or update the relevant row in `docs/logs/task-journal.md` with the new information (multiple entries per task are expected while work is in flight).
3. **Tooling Registry Update** – Add or modify rows in `docs/reference/tooling-registry.md` whenever instruments, plugins, services, or interfaces change.
4. **Project Map Update** – Reflect any filesystem changes in `docs/reference/project-map.md` during the same turn.
5. **Confirmation** – Assistant reports the logging actions taken so you always know the audit trail is current.

### Weekly (or feature completion)
- Review feedback metrics & runbooks.
- Update quickstart instructions if new flows exist.
- Tag a release and write release notes (`docs/releases/`).

---

## 4. Git Workflow for New AI Developers

1. **Branching**
   - Create feature branches: `git checkout -b feature/knowledge-ingestion`.
   - Keep branch names consistent with tasks/specs when possible.

2. **Commit Style**
   - Use present tense, concise messages: `feat: add knowledge ingestion service`.
   - Group related changes; don’t mix tests, refactors, and features in one commit.

3. **Pull Requests**
   - Open PRs early for visibility; request feedback when tests are green.
   - Summarize what changed, link to tasks, mention tests run.

4. **Conflict Avoidance**
   - Sync frequently: `git fetch --all`, `git rebase origin/main`.
   - Resolve conflicts ASAP; ask for help if they touch unfamiliar areas.

---

## 5. Working With Spec Kit Assets

| File | Purpose | Tips |
|------|---------|------|
| `.specify/memory/constitution.md` | Governance rules | Check before major architectural decisions. |
| `.specify/templates/*.md` | Baseline templates | Don’t edit directly; copy if you need new variants. |
| `specs/main/spec.md` | Feature requirements | Keep updated with new clarifications. |
| `specs/main/plan.md` | Implementation plan | Update Progress Tracking as you finish phases. |
| `specs/main/tasks.md` | Execution list | Check items off as you go (keep history in commits/PRs). |
| `docs/manual/working-with-spec-kit.md` | This guide | Update if the workflow evolves. |

**Key Principle:** Never skip the constitution check. Every change must respect multi-domain excellence, knowledge traceability, learning architecture, courtesy, output flexibility, performance measurement, and text-only interface.

---

## 6. Starting the Build (Sales Focus)

1. **Set up environment (T001–T012)**
   - Install Python 3.11, Docker, PostgreSQL, Redis.
   - Initialize the FastAPI project, configure linting, create `.env` from `.env.example`.
   - Run initial lint/test commands to confirm the scaffolding works.

2. **Write baseline tests (T013–T025)**
   - Flesh out pytest setup, create failing contract tests for core APIs.
   - Add unit tests for config, vector store, personality detection, etc.

3. **Implement knowledge ingestion (T026–T038)**
   - Build the ingestion pipeline, concept extraction, embeddings, vector repository.
   - Expose the knowledge API and seed initial sources (sales psychology, car specs, communication guide).

4. **Continue through tasks sequentially**
   - Customer intelligence (T039+)
   - Recommendation engine (T049+)
   - Feedback/analytics (T061+)
   - Security/integration/QA (T068+)

Commit at meaningful checkpoints (e.g., after T038 is fully passing). Keep the constitution checklist in `plan.md` updated if decisions change.

---

## 7. Communication & Decision Logging
- Maintain a `docs/notes/decision-log.md` for architectural or process decisions (create it on first use).
- Use TODO comments sparingly and link them to task IDs (e.g., `# TODO(T052): refine prompt template once data is available`).
- If we revise templates or constitution, record the version change and rationale.

---

## 8. Troubleshooting & Escalation
- **Build issues**: Check `docs/runbooks/` once we populate them; otherwise, record new fixes there.
- **Spec gaps**: Return to spec/plan files, add clarifications, and notify via commit message.
- **Performance regressions**: Run the load tests (T075). If they fail, pause new features until resolved.
- **Knowledge ingestion errors**: Inspect worker logs, verify document formats, ensure embeddings service is reachable.

---

## 9. Mindset & Best Practices Recap
- **Test-Driven**: Write tests before implementation. Keep coverage meaningful.
- **Incremental**: Small, reviewable changes beat giant refactors.
- **Traceable**: Every recommendation must be explainable. Preserve source links.
- **Document As You Go**: Future you (and teammates) will thank you.
- **Stay Constitutional**: The governance rules aren’t optional.

---

## 10. Ready To Build? Immediate Action Items
1. Clone the repo and run `git status` to ensure a clean working tree.
2. Complete Phase 3.1 tasks (environment + scaffolding).
3. Start Phase 3.2 tests—no production code changes until tests exist.
4. Ask for help anytime you hit uncertainty; better to clarify than rework.

Let’s go build the most knowledgeable, precise sales copilot imaginable. Keep this manual close, iterate deliberately, and we’ll ship something legendary.
