---
name: Python Development
description: Generic Python coding standards and best practices for AI agents to follow when writing or modifying Python code in this repository.
applyTo: "**/*.py"
---

# Python Development Instructions

## Style & Formatting
- Follow [PEP 8](https://peps.python.org/pep-0008/) for code style and layout.
- Use 4 spaces per indentation level; never mix tabs and spaces.
- Keep lines to a reasonable length (prefer ≤ 100 characters).
- Use `snake_case` for variables and functions, `PascalCase` for classes, and `UPPER_SNAKE_CASE` for constants.
- Prefer f-strings for string formatting over `%` or `.format()`.

## Type Hints & Documentation
- Add type hints to function signatures (parameters and return types).
- Write concise docstrings for public modules, classes, and functions describing purpose, arguments, and return values (e.g. Google or reST style) — skip docstrings for obvious/private helpers.
- Only add inline comments when the *why* isn't obvious from the code itself.

## Structure & Design
- Follow the Single Responsibility Principle — keep functions and classes focused on one task.
- Prefer small, composable functions over large monolithic ones.
- Avoid deep nesting; use early returns/guard clauses instead.
- Avoid global mutable state; pass dependencies explicitly.
- Don't introduce abstractions, helpers, or configuration options that aren't needed yet.

## Imports
- Group imports in order: standard library, third-party, local/application — separated by a blank line.
- Use absolute imports; avoid wildcard imports (`from module import *`).
- Remove unused imports.

## Error Handling
- Catch specific exceptions, never bare `except:`.
- Don't silently swallow exceptions — log or re-raise with context.
- Validate inputs only at system boundaries (user input, external APIs); trust internal code.

## Dependencies & Environment
- Pin dependencies in the relevant `requirements.txt` (or equivalent) file.
- Avoid adding new third-party dependencies unless necessary; prefer the standard library.

## Testing
- Write tests using `pytest` conventions where a test suite exists.
- Test names should describe behavior (e.g. `test_returns_empty_list_when_no_input`).
- Cover edge cases, not just the happy path.

## Security
- Never hard-code secrets, API keys, or credentials — use environment variables or a secrets manager.
- Sanitize/validate any external input before use (avoid injection risks).
- Avoid `eval()`, `exec()`, and unsafe deserialization (e.g. `pickle` on untrusted data).
