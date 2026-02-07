<!--
SYNC IMPACT REPORT
Version change: 1.0.0 → 1.1.0
List of modified principles: N/A
Added sections: "Reusable Intelligence Agent Implementation" principle
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ reviewed - Constitution Check section will include new principle
  - .specify/templates/spec-template.md ✅ reviewed - still consistent with new principles
  - .specify/templates/tasks-template.md ✅ reviewed - should now include agent-related tasks
  - .qwen/commands/sp.constitution.toml ✅ reviewed - no changes needed
Follow-up TODOs:
  - RATIFICATION_DATE still set to placeholder value
-->

# Hackathon II Phase I In-Memory Python Console Todo App Constitution

## Core Principles

### Spec-Driven Development Only
All development must follow Spec-Driven Development methodology; No manual coding without prior specification; All features must be defined in specs before implementation

### In-Memory Storage Only
Application must use in-memory storage only; No file system or database persistence; All data is volatile and exists only during runtime

### Basic 5 Features Implementation
Application must implement exactly 5 core features: Add, View, Update, Delete, Mark Complete; Each feature must be fully functional and tested

### Clean Python with Type Hints and PEP8
Code must follow PEP8 standards; All functions and variables must have proper type hints; All functions must have docstrings; Clean, readable code structure required

### No External Libraries
Application must be built using only Python standard library; No external dependencies or packages allowed; Pure vanilla Python implementation

### Modular Structure Preferred
Code must be organized in a modular structure with clear separation of concerns; CLI interface, business logic, and data models should be in separate modules; Task data must include id, title, description, and completed status

### Reusable Intelligence Agent Implementation
Create a simple reusable Todo Agent in a separate module (src/agent/todo_agent.py); The agent should accept natural language commands (e.g., 'add buy milk', 'list tasks', 'complete 2', 'delete 1'); Agent must parse the command and call appropriate TaskManager methods; Agent should be reusable and demonstrable as 'intelligence skill'; Agent logic should be rule-based (no external LLM calls needed for Phase I); Include example commands in documentation

## Additional Constraints

Task data structure: id (int), title (str), description (str), completed (bool); CLI menu loop with clear prompts and error handling; No persistent storage beyond runtime memory

## Development Workflow

Follow Spec-Driven Development cycle: Specification → Tasks → Implementation → Testing; All code changes must have corresponding tests; Code review required before merging

## Governance
All development must comply with the stated principles; Deviations require explicit approval and documentation; Code must pass all tests before acceptance; All features must be specified before implementation

**Version**: 1.1.0 | **Ratified**: 2025-01-01 | **Last Amended**: 2025-12-27
