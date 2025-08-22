# PAI
A CLI personal assistant tool for working with everyday tasks, the main selling point is that it gives users control over what models are run, where they are run, what data is used and where it goes. 

## How to run 

### Initalise session
```python
python -m PAI init openai --model gpt-4o-mini
```

### Prompt model
```python
python -m PAI prompt "What is the capital of France?"
```

### Check session status
```python
python -m PAI prompt "What is the capital of France?"
```

###  chat
```python
python -m PAI chat
Interactive chat with openai (gpt-4o-mini)
Type 'exit', 'quit', or press Ctrl+C to end

You: "What's the first wonder of the world"
AI: The term "wonders of the world" can refer to different lists, but the most famous is the Seven Wonders of the Ancient World. The first of these is the Great Pyramid of Giza in Egypt. It is the only one of the seven wonders that still exists today. If you meant a different list, such as the New Seven Wonders, please let me know!

You: exit
Chat ended!

```

### Quit session
```python
python -m PAI reset
```

### List available providers
```python
python -m PAI providers
Available Providers:
   - openai

Use 'pai init <provider> --model <model>' to initialize a session
```

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

#### Model Provider Management
- [ ] Add more model providers (Anthropic, Ollama, LM Studio, local models)
- [ ] Multi model for agent and assistant mode 

#### Misc Functionality
- [ ] Implement out-of-session commands (quick prompts without session init, limited functioanlity)

#### Engineering Good Practice
- [ ] Add unit tests + integration tests
- [ ] Add build tool (Poetry)
- [ ] Add GitHub Actions CI/CD
- [ ] Review + refactor code


### Notes
Only supports OpenAI  
Do all model providers have the capability to accept system prompts?

### How to run

Clone the repository

You need the following: 
	Python (I use 3.11 nut I think older versions should work as well)
	typer
	openai (alonmg with an active api key saved as an environment variable "OPENAI_API_KEY")

It should be OS independennt but I've only tested on windows so far.