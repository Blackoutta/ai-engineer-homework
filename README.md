# AI Homework Review System

An automated system for reviewing AI homework submissions that clones student repositories, extracts repository information, and generates detailed review reports against assignment requirements.

## Features

- **Repository Cloning**: Automatically clones GitHub repositories to temporary directories
- **Information Extraction**: Uses LLM to parse repository links and extract metadata
- **Automated Review**: Performs code review against homework requirements using AI
- **Report Generation**: Creates detailed markdown review reports
- **Logging**: Comprehensive logging for debugging and monitoring

## Prerequisites

- Python 3.11+
- Git
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- Access to LLM API services (configured via environment variables)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-engineer-homework
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp .env.example.glm .env  # or .env.example.kimi depending on your LLM service
```

Edit `.env` file with your API keys and configuration.

## Usage

### Basic Usage

```bash
python main.py --link <github_repository_url> --req <requirements_file_path>
```

### Example

```bash
python main.py --link "https://github.com/user/repo/tree/main/homework" --req "homework_requirements/week03-pt1.md"
```

This will:
1. Extract repository information from the provided link
2. Clone the repository to a temporary directory
3. Review the homework against the specified requirements
4. Generate a markdown review report in the cloned repository

### Development Mode

```bash
python -m main --link <url> --req <requirements>
```

## Architecture

The system consists of four main components:

1. **Main Entry Point** (`main.py`): Orchestrates the entire workflow
2. **Repository Extractor** (`tools/repo_extractor.py`): Parses repository links and extracts metadata
3. **Git Cloner** (`tools/cloner.py`): Handles repository cloning to temporary directories
4. **Homework Reviewer** (`tools/reviewer.py`): Performs code review and generates reports

## Project Structure

```
ai-engineer-homework/
├── main.py                 # Main entry point
├── tools/                  # Core functionality modules
│   ├── cloner.py          # Git cloning functionality
│   ├── repo_extractor.py  # Repository information extraction
│   └── reviewer.py        # Homework review and report generation
├── prompts/               # LLM prompt templates
├── tests/                 # Test files
├── homework_requirements/ # Homework requirement documents
├── tmp/                   # Temporary directory (created at runtime)
└── README.md             # This file
```

## Testing

Run tests using pytest:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/cloner_test.py

# Run tests with coverage
pytest --cov=tools
```

## Environment Configuration

The system uses environment variables loaded via `python-dotenv`:

- `.env`: Main environment configuration file
- `.env.example.glm`: Example configuration for GLM LLM service
- `.env.example.kimi`: Example configuration for Kimi LLM service

Required environment variables typically include:
- LLM API keys
- LLM service endpoints
- Other service configurations

## Output

The system generates a markdown review report in the cloned repository directory with the format `homework-review-YYYYMMDDHHMMSS.md`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.