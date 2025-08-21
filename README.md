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

### To-Do

#### Audit, secutriy, testing
- [ ] Add audit trail
- [ ] Add testing
- [ ] Validation steps
- [ ] Security Review
- [ ] Safe mode (enhanced permissions, policy layer)

#### Functionality 
- [ ] Add more providers
- [ ] Add tools and infrastructure for running them
- [ ] Context management for LLMs
- [ ] Add out of session commands

#### Engineering Good Practice
- [ ] Add build tool (poetry)
- [ ] Add Github Actions for CI/CD
- [ ] Review code


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