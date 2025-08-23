import typer
from PAI.commands.chat import chat_app
from PAI.commands.prompt import prompt_app
from PAI.commands.providers import providers_app
from PAI.commands.config import config_app
from PAI.commands.auth import auth_app
from PAI.commands.test import test_app
from PAI.commands.models import models_app

app = typer.Typer(help="Personal AI Interface - Initialize once, prompt many times")

app.add_typer(chat_app, name='chat')
app.add_typer(prompt_app, name='prompt')
app.add_typer(providers_app, name="providers")
app.add_typer(config_app, name="config")
app.add_typer(auth_app, name="auth")
app.add_typer(test_app, name="test")
app.add_typer(models_app, name="models")

if __name__ == "__main__":
    app()