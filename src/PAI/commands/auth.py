from __future__ import annotations
import getpass, typer
from PAI.core.config import _get_keyring_key

auth_app = typer.Typer(help="Manage API keys in your OS keychain")

@auth_app.command("set")
def set_key(provider: str):
    try:
        import keyring
    except Exception:
        raise typer.Exit(code=1)
    key = getpass.getpass(f"Enter API key for {provider}: ")
    keyring.set_password("pai", f"{provider.lower()}_api_key", key)
    typer.echo("Saved to keychain.")

@auth_app.command("clear")
def clear_key(provider: str):
    try:
        import keyring
        keyring.delete_password("pai", f"{provider.lower()}_api_key")
        typer.echo("Cleared from keychain.")
    except Exception:
        typer.echo("No key to clear or keyring not available.")
