# PAI

A CLI personal assistant for everyday tasks. The goal is to give you control over which models run, where they run, what data is used, and where that data goes.

## Requirements

- Python 3.11 or newer
- [Poetry](https://python-poetry.org/) installed
- An API key for your chosen provider (currently OpenAI). For OpenAI, set `OPENAI_API_KEY` in your environment
- An encryption key `PAI_ENCRYPTION_KEY` stored as an environment variable to ensure safe storage of api keys. See instructions below on how to generate.
  
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

## Get encryption keys
PAI uses encryption to store sensitive data like API keys. 

To generate an encryption key, run the following Python snippet and set this as the `PAI_ENCRYPTION_KEY` environment variable. 

```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(key.decode())  # This prints a base64-encoded string you can use as your encryption key
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

#### API Key Storage and Usage

PAI supports two ways to provide API keys for model providers:

1. **Environment Variable (Recommended):**
   - Set your API key as an environment variable (e.g., `OPENAI_API_KEY`).
   - If no API key is provided during session initialization, PAI will automatically use the environment variable.

2. **Session Storage (Optional):**
   - You may supply an API key directly when initializing a session.
   - If provided, the API key is **encrypted** before being saved to disk using Fernet symmetric encryption.
   - The encryption key must be set as the `PAI_ENCRYPTION_KEY` environment variable.
   - When loading a session, the API key is decrypted and used for provider authentication.

**Security Note:**  
API keys stored in session files are always encrypted and are stored outside of the git repo in your home directly (can be ammended but is not recommended). 
For maximum security, prefer environment variables and avoid sharing session files containing sensitive information. 


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
poetry run pai init <session name> openai --model gpt-4o-mini
```

Send a one-off prompt:
```bash
poetry run pai <session name> prompt "What is the capital of France?"
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

### Running unit tests
```bash
poetry run pytest
```

### Running modes

#### 1. Chat Mode
- **Purpose**: Lightweight conversational interface.
- **Context**: Maintains full session chat history, cleared on reset.
- **Resources**: Minimal.
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
Same as prompt but unbounded 

### To-Do

#### Context Management
- [x] Build context manager as a single interface for tools and resources
- [x] Implement contextmanager prompt in PAI.generate 
- [x] Build session-level context manager (contains chat history, clears on reset)
- [x] Implement PromptMode context (resource usage, limited reprompts)
- [ ] Implement tool/ resource caching in context manager (Maybe not, limiting tokens might be more important than compute)
- [ ] Implement AgentMode context (unlimited reprompt → tool → re-prompt loops)
- [ ] Add token usage tracking + limits (FinOps-style budget)

#### Resource Management
- [x] Make resource manager (similar to tool manager))
- [x] Create resource storage (JSON)
- [x] Expose resource metadata to model using context manager
- [x] Add resource interactions (CRUD operations)
- [x] Implement resource retrieval
- [ ] Refactor resource strategy for very large resources repositories.  (We currently read all resources into memeory in order to avoid duplication and find resources, solve when I get round to it)
- [ ] Implement resource request API for LLM/tool usage (for things like external S3 buckets)
- [ ] Define resource interaction with  llm per running mode (chat, prompt, agent)
- [ ] Fix extract resource 

#### Policy Management
- [ ] Create policy manager (similar to tool manager, scan prompts for policy adherence)
- [ ] Enforce tool/resource safety via policy rules 
- [ ] Conduct security review (permissions, sandboxing, policy validation)

#### Tool Management
- [x] Expose tool register to model using context manager
- [ ] Add more tools (file system, web scraping, API calls, database access)
- [x] Implement loop for sucessive tool chaining (include cli optional parameter to limit number for prompt mode)
- [ ] Fix extract tool method


#### Audit, Security
- [x] Log all prompts, tool calls, resource accesses, model responses
- [x] Include metadata: who, when, model/provider, token usage
- [ ] Session constraints (tools, resources available)
- [x] Ensure audit logs are secure and queryable (check where is the best place to store them)
- [ ] Validation steps
- [ ] Security review
- [ ] Safe mode (enhanced permissions, policy layer)

#### Model Provider Management
- [ ] Add more model providers (Ollama, LM Studio, local models)
- [x] Function in PAI to switch models in a session
- [ ] Multi model for agent and assistant mode 
- [ ] Add retry and wait logic for rate limit handling

#### Misc Functionality

#### Engineering Good Practice
- [x] Add unit tests + integration tests
- [x] Add build tool (Poetry)
- [x] Add GitHub Actions CI/CD
- [x] Ammend Build_and_Lint to use poetry build rather than requirements.txt
- [ ] Review + refactor code
- [x] Obsfucate api keys in logs (if provided)
- [ ] Resource handling / RAG → Embed large resources for retrieval; read small ones directly.
- [ ] Concurrency / file locks → Lock session log during writes with retries; reads safe.
- [ ] Optional caching / daemon → Speed up repeated interactions; keep CLI stateless.
- [ ] Zero-dependency packaging → Distribute as wheel or self-contained executable.

### Notes
Think about creating a DSL for tool calling, resource acces and softt policy instructions. 

## Licence
MIT
