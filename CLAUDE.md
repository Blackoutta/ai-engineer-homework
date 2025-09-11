# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI homework review system that automates the process of cloning student repositories, extracting repository information, and reviewing homework submissions against requirements. The system processes GitHub repository links, clones them to temporary directories, and generates markdown review reports.

## Key Commands

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/cloner_test.py

# Run tests with coverage
pytest --cov=tools
```

### Running the Application
```bash
# Main entry point - requires --link and --req arguments
python main.py --link <github_repository_url> --req <requirements_file_path>

# Example usage
python main.py --link "https://github.com/user/repo/tree/main/homework" --req "homework_requirements/week03-pt1.md"
```

### Development
```bash
# Install dependencies (uses uv package manager)
uv sync

# Run in development mode
python -m main --link <url> --req <requirements>
```

## Architecture

### Core Components

1. **Main Entry Point** (`main.py`)
   - Orchestrates the entire workflow
   - Handles argument parsing and logging setup
   - Coordinates between cloner, extractor, and reviewer components

2. **Repository Extraction** (`tools/repo_extractor.py`)
   - Uses LLM to parse repository links and extract metadata
   - Identifies repository URL, branch, and user homework directory
   - Calls external LLM service via `_call_llm()` method

3. **Git Cloning** (`tools/cloner.py`)
   - Handles repository cloning to temporary directories
   - Supports optional branch specification
   - Validates repository URLs and target directories

4. **Homework Review** (`tools/reviewer.py`)
   - Performs code review against homework requirements
   - Generates markdown review reports
   - Uses LLM prompts for evaluation

### Directory Structure

- `tools/`: Core functionality modules
- `prompts/`: LLM prompt templates for extraction and review
- `tests/`: Test files (pytest-based)
- `homework_requirements/`: Homework requirement documents
- `tmp/`: Temporary directory for cloned repositories (created at runtime)

### Environment Configuration

The project uses environment variables loaded via `python-dotenv`:
- Configuration files: `.env`, `.env.example.glm`, `.env.example.kimi`
- Required for LLM API access and other external services

## Testing Strategy

- Tests are written using pytest
- Main test coverage focuses on the GitCloner functionality
- Tests are located in the `tests/` directory
- Coverage reports can be generated with `pytest --cov`

## Development Notes

- Uses Python 3.11+ as specified in `pyproject.toml`
- Virtual environment managed with uv package manager
- Logging is configured at the INFO level with timestamps
- Temporary directories use timestamp-based naming to avoid conflicts
- The system creates review reports in markdown format in the cloned repository directory

## Important Implementation Details

- The `_call_llm()` methods in both extractor and reviewer are critical components that interface with external LLM services
- Error handling is implemented with try-catch blocks and logging
- The workflow is sequential: extract → clone → review
- All components accept optional logger instances for consistent logging