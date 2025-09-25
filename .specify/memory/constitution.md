<!--
Sync Impact Report:
Version change: v1.5.0 → v1.6.0
Modified principles: None
Added sections:
  - Automated Logging Workflow in Governance
Removed sections: None
Templates requiring updates: ✅ docs/manual/working-with-spec-kit.md | ✅ docs/logs/task-journal.md | ✅ docs/reference/project-map.md | ✅ docs/reference/tooling-registry.md | ✅ docs/logs/README.md (create)
Follow-up TODOs: None
-->

# Sales Assistant Constitution

## Core Principles

### I. Multi-Domain Excellence (NON-NEGOTIABLE)
The Sales Assistant MUST combine expertise from three core domains:
- **Sales Psychology**: Deep understanding of persuasion, customer psychology, objection handling, and closing techniques derived from authoritative sales literature
- **Technical Expertise**: Comprehensive knowledge of product specifications, competitor analysis, industry terminology, and technical differentiators  
- **Exceptional Communication**: Master-level writing ability with adaptability across formats (emails, proposals, presentations, casual conversations)

**Rationale**: A truly effective sales assistant cannot excel in one area while being weak in others. Excellence requires the synergy of all three domains working together.

### II. Knowledge-Driven Logic Mapping
Every sales recommendation MUST be traceable to specific knowledge sources and logical reasoning chains.
- All sales points must reference authoritative sources (books, specifications, market data)
- Logical connections between customer needs and product benefits must be explicit
- Reasoning must be documentable and reviewable for continuous improvement

**Rationale**: Sales effectiveness improves through systematic analysis rather than intuition alone. Traceable logic enables learning and refinement.

### III. Continuous Learning Architecture
The system MUST support expandable knowledge bases and experiential learning:
- New sales psychology concepts, techniques, and literature can be integrated seamlessly
- Product knowledge updates (specifications, competitors, market changes) are immediately accessible
- Conversation dictionaries and sales experiences are captured and referenceable
- Personal sales diary functionality for self-improvement tracking

**Rationale**: Sales environments change rapidly. Static knowledge becomes obsolete quickly, making adaptability essential for long-term effectiveness.

### IV. Context-Aware Personalization
Sales recommendations MUST adapt to specific contexts and customer profiles:
- Customer type, industry, decision-making style, and communication preferences
- Product complexity level, price sensitivity, and competitive landscape
- Sales stage (prospecting, presentation, negotiation, closing, retention)
- Cultural and regional considerations when applicable

**Rationale**: Generic sales approaches fail. Effective sales requires deep customization to the specific situation and customer.

### V. Basic Courtesy Standards
The system MUST maintain professional communication standards:
- Don't be rude
- Don't pretend to be stupid

**Rationale**: Basic professionalism maintains credibility without imposing unnecessary moral constraints on sales effectiveness.

### VI. Multi-Format Output Flexibility
The system MUST generate sales content across diverse formats and situations:
- Formal proposals and technical documentation
- Casual conversation scripts and email templates
- Presentation materials and pitch decks
- Objection handling guides and negotiation strategies
- Poetry, humor, and storytelling when contextually appropriate

**Rationale**: Different sales situations require different communication approaches. Rigid formats limit effectiveness across diverse sales contexts.

### VII. Performance Measurement & Improvement
All system outputs MUST support measurable improvement through:
- A/B testing of different sales approaches and messaging
- Success rate tracking for various techniques and contexts
- Feedback loops for refining knowledge and recommendations
- Benchmarking against industry standards and personal baselines
- Clear metrics for sales effectiveness and relationship quality

**Rationale**: What cannot be measured cannot be systematically improved. Sales performance requires data-driven optimization.

## Knowledge Architecture

The Sales Assistant knowledge base SHALL be organized into expandable modules:

**Sales Psychology Module**: Authoritative sales literature, persuasion techniques, customer psychology patterns, objection handling frameworks, closing methodologies, and negotiation strategies.

**Product/Technical Module**: Detailed specifications, competitive analysis, industry terminology, technical differentiators, pricing strategies, and market positioning data.

**Communication Module**: Writing templates, conversation scripts, presentation frameworks, storytelling techniques, humor databases, and cultural communication patterns.

**Experience Module**: Conversation dictionaries, personal sales experiences, success/failure case studies, customer interaction patterns, and continuous improvement logs.

## User Experience Standards

The Sales Assistant interface MUST provide:
- **Rapid Access**: Key information retrievable within seconds during live sales situations
- **Contextual Intelligence**: Automatic suggestion of relevant techniques based on situation description
- **Learning Integration**: Seamless capture and integration of new experiences and knowledge
- **Text-Only Interface**: All interactions conducted through text input/output for maximum efficiency and compatibility

## Governance

This constitution supersedes all other development practices and design decisions. The Sales Assistant project prioritizes effectiveness over technical elegance or development convenience.

**Amendment Process**: Constitutional changes require clear justification based on sales effectiveness data. All amendments must maintain consistency with core principles.

**Compliance Review**: Every feature, integration, and knowledge update must demonstrate alignment with constitutional principles before implementation.

**Interaction Command Processing Protocol**: Every user-issued command or suggestion MUST be handled with the following workflow:
1. **Classify the request** → Determine whether it is a clarification, specification update, planning adjustment, task execution change, or implementation action.
2. **Check prerequisites** → Verify that required artifacts (clarifications, spec, plan, tasks) exist and are current for the request type. Halt and request missing prerequisites before proceeding.
3. **Document the decision** → Record the outcome in the appropriate artifact (clarification notes, spec, plan, tasks, or decision log) before executing substantive work.
4. **Execute & report** → Carry out the agreed steps, then respond with a concise summary, updated status, and explicit next actions.

**Task Completion Journal**: Upon completing any task from `tasks.md`, the team MUST log the following in `docs/logs/task-journal.md` before moving on:
- Task ID and description
- Artifacts touched (files, templates, docs)
- Prompts, commands, or clarifications used to reach completion
- Decision notes or follow-up items

**Project Knowledge Map**: The team MUST maintain an up-to-date repository map at `docs/reference/project-map.md`. Update this map whenever new modules, directories, or significant files are added or materially changed so the assistant can rely on definitive structure instead of inference.

**Verification Evidence Rule**: No task may be marked complete until the team captures explicit verification evidence in the task journal. Record the tests, scripts, or manual checks executed, the command(s) run, and their outcomes (pass/fail with error summaries). If validation is intentionally deferred, the deferral rationale and owner MUST be logged, and the task remains blocked until verification passes.

**Tooling Alignment Protocol**: Before initiating implementation work for any phase, the team MUST agree on the instruments, plugins, external services, and interface layers to be used. Log the decision in `docs/reference/tooling-registry.md`, including access credentials management strategy, version/pinning details, and any compatibility notes. Deviations require prior review and registry updates before changes begin.

**Code Synchronization Safeguards**: To minimize merge conflicts and regressions, every contributor MUST (a) pull/rebase from the trunk branch at the start of each work session, (b) limit active work-in-progress to one open task at a time, (c) signal task ownership in the task journal before coding, and (d) run agreed quality gates (tests, lint, format) prior to merging. Violations block task completion until corrected.

**Automated Logging Workflow**: After every confirmed implementation action, the team MUST immediately capture the prompt, assistant response summary, and resulting artifacts using the `/log-latest` command. This workflow requires: (a) appending an entry to `docs/logs/task-journal.md` (even if the task is ongoing) with current status and verification evidence, (b) updating `docs/reference/tooling-registry.md` when tooling/services change, and (c) reflecting structural adjustments in `docs/reference/project-map.md`. No subsequent work may begin until these logs are updated.

**Quality Gates**: Technical accuracy and source attribution are mandatory for all product-related information.

Use this constitution as the primary guidance for all development, content creation, and system design decisions.

**Version**: v1.6.0 | **Ratified**: 2025-09-24 | **Last Amended**: 2025-09-24