# PAI

A CLI personal assistant for everyday tasks. The goal is to give you control over which models run, where they run, what data is used, and where that data goes.

## Requirements

- Python 3.11 or newer
- [Poetry](https://python-poetry.org/) installed
- An API key for your chosen provider (currently OpenAI). For OpenAI, set `OPENAI_API_KEY` in your environment

## Install Poetry

The simplest way is the official installer.

**macOS/Linux**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Alternative (macOS Homebrew)**
```bash
brew install poetry
```

**Windows (PowerShell)**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

**Verify**
```bash
poetry --version
```


## Quickstart with Poetry

```bash
# Optional: put the virtualenv inside the project folder as .venv
poetry config virtualenvs.in-project true --local
# From the repo root
poetry install

# Run commands without leaving your shell
poetry run pai --help
```

### Configure your API key

Mac/Linux (bash/zsh):
```bash
export OPENAI_API_KEY="sk-..."
```

Windows PowerShell:
```powershell
$env:OPENAI_API_KEY = "sk-..."
```

## Usage

Initialise a session (OpenAI example):
```bash
poetry run pai init openai --model gpt-4o-mini
```

Send a one-off prompt:
```bash
poetry run pai prompt "What is the capital of France?"
```

Check session status:
```bash
poetry run pai status
```

Interactive chat:
```bash
poetry run pai chat
# Type 'exit' or 'quit' (or press Ctrl+C) to end
```

Reset the session:
```bash
poetry run pai reset
```

List available providers:
```bash
poetry run pai providers
# Example output:
# Available Providers:
#    - openai
#
# Use 'pai init <provider> --model <model>' to initialize a session
```

### Alternate invocation
If you prefer the module form, this also works:
```bash
poetry run python -m PAI --help
```
## To-Do

### Audit, security, testing
- [ ] Add audit trail
- [ ] Add testing
- [ ] Validation steps
- [ ] Security review
- [ ] Safe mode (enhanced permissions, policy layer)

### Functionality
- [ ] Add more providers
- [ ] Add tools and infrastructure for running them
- [ ] Context management for LLMs
- [ ] Add out-of-session commands

### Engineering good practice
- [x] Add build tool (poetry)
- [ ] Add GitHub Actions for CI/CD
- [ ] Review code

## Notes
- Currently supports OpenAI
- Do all model providers have the capability to accept system prompts?

## Licence
MIT
