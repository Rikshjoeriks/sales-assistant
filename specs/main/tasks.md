# Tasks: UI Cleanup and Workflow Centralization

**Input**: Design documents from `/specs/main/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: N/A
   → contracts/: N/A
   → research.md: N/A
3. Generate tasks by category:
   → Setup: project analysis
   → Tests: N/A (manual testing)
   → Core: UI refactoring, button removal
   → Integration: workflow centralization
   → Polish: testing, documentation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD) - N/A
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All redundants removed?
   → Workflow centralized?
   → No breaking changes?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: Repository root
- Paths shown below assume repository root structure

## Phase 3.1: Setup
- [ ] T001 Analyze current UI structure in ui.py to identify all analysis buttons and handlers

## Phase 3.2: Tests First (TDD) ⚠️ MANUAL TESTING ONLY
**CRITICAL: Manual testing required before and after changes**
- [ ] T002 [P] Manual test: Verify SpecMatcher launches successfully
- [ ] T003 [P] Manual test: Verify "Learning MEGA 3x" button works correctly
- [ ] T004 [P] Manual test: Verify export functions work

## Phase 3.3: Core Implementation (ONLY after tests are verified)
- [ ] T005 Map all analysis buttons and their handlers in ui.py
- [ ] T006 Document the 'Learning MEGA 3x' button as the canonical workflow
- [ ] T007 Remove redundant analysis buttons (Run pipeline, Run dual pipeline, Run intelligent, Run MEGA, etc.)
- [ ] T008 Centralize prompt handling through Learning workflow only
- [ ] T009 Deduplicate result processing code across different handlers

## Phase 3.4: Integration
- [ ] T010 Update any references to removed buttons in other files
- [ ] T011 Ensure learning_dictionary.db and feature_dictionary.db remain functional

## Phase 3.5: Polish
- [ ] T012 [P] Manual test: Verify simplified workflow works end-to-end
- [ ] T013 [P] Manual test: Verify no breaking changes in functionality
- [ ] T014 Document remaining legacy code for future removal
- [ ] T015 Update any documentation files (README, etc.) to reflect changes

## Dependencies
- T001 before T005-T009
- T002-T004 before T005-T015
- T005-T009 before T010-T011
- T010-T011 before T012-T015

## Parallel Example
```
# Launch T002-T004 together:
Task: "Manual test: Verify SpecMatcher launches successfully"
Task: "Manual test: Verify 'Learning MEGA 3x' button works correctly"
Task: "Manual test: Verify export functions work"
```

## Notes
- [P] tasks = different files, no dependencies
- Manual testing is critical since no automated tests exist
- Commit after each task
- Focus on preserving functionality while simplifying UI

## Task Generation Rules
- Each redundant button → removal task
- Each workflow duplication → deduplication task
- Manual testing for each major change</content>
<parameter name="filePath">c:\Users\vanag\Documents\INCHCAPE\SMATCH\spec_matcher\specs\main\tasks.md
