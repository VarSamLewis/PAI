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
### Running modes

#### 1. Chat Mode
- **Purpose**: Lightweight conversational interface.
- **Context**: Maintains full session chat history, cleared on reset.
- **Resources**: Minimal (default resources only, no CRUD).
- **Tools**: Limited to safe/basic tools, no chaining.
- **Policies**: Pre-scan of prompts, basic safety rules applied.
- **Audit**: Log all interactions with metadata.

#### 2. Prompt Mode
- **Purpose**: Focused, bounded prompt execution with summary + resource usage.
- **Context**: Session summary retained, limited reprompts allowed.
- **Resources**: Read-only access to resources; request API allowed for external data.
- **Tools**: Limited execution of tools with optional CLI flag to cap chaining depth.
- **Policies**: Policy manager validates prompts/resources before execution.
- **Audit**: Log prompts, responses, resource/tool usage; track token budget.

#### 3. Agent Mode
- **Purpose**: Autonomous loop of reasoning and acting (prompt → tool → reprompt).
- **Context**: Full session reasoning context; multiple re-prompts allowed.
- **Resources**: CRUD access to resources; can interact with external storage (S3, DBs).
- **Tools**: Successive tool chaining enabled; tool manager enforces constraints.
- **Policies**: Strong enforcement of tool/resource safety rules.
- **Audit**: Logs include tool chains, resource CRUD, session constraints.

#### 4. Assistant Mode
- **Purpose**: Long-lived assistant performing continuous execution.
- **Context**: Persistent across tasks; maintains working memory until session end/reset.
- **Resources**: Full CRUD access; can orchestrate multiple resources.
- **Tools**: Tool chaining with minimal limits; external venv for isolated tool execution.
- **Policies**: Strong security/sandboxing, policy enforcement required.
- **Audit**: Continuous tracking of actions, token usage, and outcomes.

### To-Do

#### Context Management
- [ ] Build session-level context manager (clears on reset)
- [ ] Implement ChatMode context (full chat history)
- [ ] Implement PromptMode context (session summary, resource usage, limited reprompts)
- [ ] Implement AgentMode context (unlimited reprompt → tool → re-prompt loops)
- [ ] Implement AssistantMode context (continuous execution)
- [ ] Implement All-InMode context (agent + full session memory)?
- [ ] Add token usage tracking + limits (FinOps-style budget)

#### Resource Management
- [ ] Make resource manager (similar to tool manager))
- [ ] Create resource storage (JSON)
- [ ] Implement resource retrieval 
- [ ] Implement resource request API for LLM/tool usage (for things like external S3 buckets)
- [ ] Add resource interactions (CRUD operations)
- [ ] Define resource interaction with  llm per running mode (chat, prompt, agent, assistant)

#### Policy Management
- [ ] Create policy manager (similar to tool manager, scan prompts for policy adherence)
- [ ] Enforce tool/resource safety via policy rules 
- [ ] Conduct security review (permissions, sandboxing, policy validation)

#### Tool Management
- [ ] Add more tools (file system, web scraping, API calls, database access)
- [ ] Implement loop for sucessive tool chaining (include cli optional parameter to limit number for prompt mode)
- [ ] Create venv for tool execution (isolate from main process, library dependicies)?

#### Audit, Security
- [ ] Log all prompts, tool calls, resource accesses, model responses
- [ ] Include metadata: who, when, model/provider, token usage
- [ ] Session constraints (tools, resources available)
- [ ] Ensure audit logs are secure and queryable
- [ ] Validation steps
- [ ] Security review
- [ ] Safe mode (enhanced permissions, policy layer)

#### Model Provider Management
- [ ] Add more model providers (Anthropic, Ollama, LM Studio, local models)
- [ ] Multi model for agent and assistant mode 

#### Misc Functionality
- [ ] Implement out-of-session commands (quick prompts without session init, limited functioanlity)

#### Engineering Good Practice
- [ ] Add unit tests + integration tests
- [x] Add build tool (Poetry)
- [ ] Add GitHub Actions CI/CD
- [ ] Review + refactor code

### Notes
Only supports OpenAI  
Do all model providers have the capability to accept system prompts?

## Licence
MIT
