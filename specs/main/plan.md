
# Implementation Plan: Core Knowledge Ingestion & Sales Content Generation

**Branch**: `main` | **Date**: 2025-09-24 | **Spec**: [specs/main/spec.md](./spec.md)
**Input**: Feature specification from `C:\Users\vanag\Documents\SALESASSISTANT\specs\main\spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Core knowledge ingestion system that combines sales psychology literature, automotive technical specifications, and communication guides to generate personalized sales recommendations via ChatGPT API integration. System processes customer context to deliver tailored talking points with source attribution across multiple output formats.

## Technical Context
**Language/Version**: Python 3.11  
**Primary Dependencies**: OpenAI API (ChatGPT), FastAPI, SQLite/PostgreSQL, Pydantic, requests  
**Storage**: SQLite for development, PostgreSQL for production (knowledge bases, interaction logs, customer profiles)  
**Testing**: pytest, pytest-asyncio for API testing  
**Target Platform**: Linux server, Docker containerized  
**Project Type**: single (backend API with CLI interface)  
**Performance Goals**: <2s response time for sales recommendations, support 100 concurrent users  
**Constraints**: API rate limits (ChatGPT), knowledge base size <10GB initially, text-only interface  
**Scale/Scope**: 3 initial knowledge sources, 5-10 car models, expandable architecture for additional sources

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Multi-Domain Excellence**: ✅ **CONFIRMED** - Architecture integrates sales psychology (persuasion database), technical expertise (automotive specs), AND communication excellence (multi-format generation)  
**Knowledge Traceability**: ✅ **CONFIRMED** - SourceReference entity ensures all recommendations traceable to specific concepts and page references  
**Learning Architecture**: ✅ **CONFIRMED** - InteractionFeedback system captures outcomes, effectiveness analytics enable continuous improvement  
**Context Awareness**: ✅ **CONFIRMED** - CustomerProfile + SalesContext entities provide comprehensive personalization framework  
**Basic Courtesy**: ✅ **CONFIRMED** - Professional communication standards maintained in all generated content  
**Output Flexibility**: ✅ **CONFIRMED** - Multi-format generation (email, bullet, script, presentation) built into recommendation API  
**Performance Measurement**: ✅ **CONFIRMED** - Effectiveness tracking, analytics endpoints, A/B testing capability designed  
**Text-Only Interface**: ✅ **CONFIRMED** - All APIs designed for text input/output, CLI and REST interfaces only

**POST-DESIGN CONSTITUTION CHECK: ALL PRINCIPLES SATISFIED ✅**

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: [DEFAULT to Option 1 unless Technical Context indicates web/mobile app]

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:

**Based on Research Decisions**: Python 3.11 + FastAPI for API layer, PostgreSQL with vector extensions, ChatGPT API integration, comprehensive testing with pytest

**Based on Data Model**: 7 core entities (KnowledgeSource, KnowledgeConcept, CustomerProfile, SalesContext, SalesRecommendation, SourceReference, InteractionFeedback) requiring full CRUD operations and vector search capabilities

**Based on API Contracts**: 3 major service areas:
- Knowledge Management API (12 endpoints for source ingestion and search)
- Recommendations API (8 endpoints for generation and feedback)  
- Customer Management API (10 endpoints for profiles and interactions)

**Task Categories & Approach**:
- **Setup**: Project scaffolding, dependency management, database schema with vector extensions
- **Knowledge Processing**: PDF parsing, concept extraction, embedding generation, semantic search
- **Customer Intelligence**: Profile management, personality assessment, interaction tracking
- **Recommendation Engine**: Multi-domain integration, ChatGPT prompt engineering, source attribution
- **API Layer**: FastAPI endpoints, authentication, error handling, rate limiting
- **Learning System**: Feedback processing, effectiveness analytics, continuous improvement

**Constitutional Compliance Integration**:
- Multi-domain excellence validation in recommendation pipeline
- Knowledge traceability enforcement through source attribution
- Text-only interface adherence across all endpoints
- Performance measurement built into feedback system

**Parallelization Opportunities**:
- Knowledge source processing (by type: psychology, technical, communication)
- Customer management system (independent of knowledge processing)
- API endpoint development (after core services complete)
- Testing framework development (parallel with implementation)

**Dependency Ordering**:
- Database schema → Model classes → Repository layer → Service layer → API layer
- Knowledge processing pipeline → Recommendation engine → Feedback system
- Authentication system → API endpoint protection → Rate limiting

**Estimated Task Breakdown**:
- Setup & Infrastructure: 8 tasks
- Knowledge Processing Pipeline: 15 tasks
- Customer Management System: 10 tasks  
- Recommendation Engine: 12 tasks
- API Development: 10 tasks
- Testing & Integration: 8 tasks
- **Total Estimated**: 63 numbered, sequenced tasks

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - ChatGPT API integration strategy, knowledge processing pipeline, multi-domain architecture defined
- [x] Phase 1: Design complete (/plan command) - Data model with 7 entities, 3 API contract areas, comprehensive quickstart guide
- [x] Phase 2: Task planning complete (/plan command) - 63-task breakdown across 6 categories with dependency mapping
- [ ] Phase 3: Tasks generated (/tasks command) 
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS - All 8 constitutional principles satisfied
- [x] Post-Design Constitution Check: PASS - Multi-domain excellence, knowledge traceability, and learning architecture confirmed
- [x] All NEEDS CLARIFICATION resolved - Feature spec includes comprehensive clarifications session
- [x] Complexity deviations documented - No constitutional violations requiring justification

**Artifacts Generated**:
- [x] research.md - Technical API research, architecture decisions, risk assessment
- [x] data-model.md - 7 core entities with relationships and vector search design  
- [x] contracts/ - 3 API contract files (knowledge, recommendations, customers)
- [x] quickstart.md - Complete integration guide with examples and testing scenarios

**Ready for /tasks command execution**

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
