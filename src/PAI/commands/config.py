from __future__ import annotations
import typer
from PAI.core.config import write_user_settings, read_settings

config_app = typer.Typer(help="Configure PAI (no secrets stored).")

@config_app.command("show")
def show():
    s = read_settings()
    typer.echo(f"provider={s.provider or '(default)'}  model={s.model or '(default)'}  auth_source={s.auth_source}")

@config_app.command("set")
def set_opt(
    provider: str = typer.Option(None, "--provider"),
    model: str    = typer.Option(None, "--model"),
    auth_source: str = typer.Option(None, "--auth-source", help="auto|keyring|env"),
):
    if auth_source and auth_source not in {"auto", "keyring", "env"}:
        raise typer.BadParameter("auth-source must be auto|keyring|env")
    write_user_settings(provider=provider, model=model, auth_source=auth_source)
    show()
