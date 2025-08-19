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
- [ ] Add more providers
- [ ] Add tools and infrastructure for running them
- [ ] Add build tool (poetry)
- [ ] Add testing
- [ ] Add logging
- [ ] Add audit trail
- [ ] Add out of session commands

### Notes
GPT-5 doesn't work yet as some of the parameters are different.