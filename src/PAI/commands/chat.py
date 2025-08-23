from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional

import typer

from PAI.core.config import resolve_provider_model
from PAI.core.session import ChatSession  # owns messages, saving, switching

chat_app = typer.Typer(help="Chat commands (interactive session, optional saving).")


# -------- helpers --------

def _sessions_dir() -> Path:
    base = Path(os.environ.get("PAI_HOME") or (Path.home() / ".pai"))
    path = base / "sessions"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _list_saved_sessions() -> list[str]:
    return sorted(p.stem for p in _sessions_dir().glob("*.json"))


def _print_msg(role: str, content: str, ts: float):
    stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
    who = "you" if role == "user" else "assistant" if role == "assistant" else role
    typer.echo(f"[{stamp}] {who}> {content}")


# -------- default behaviour: `pai chat` starts a chat --------

@chat_app.callback(invoke_without_command=True)
def _default(
    ctx: typer.Context,
    save: bool = typer.Option(False, "--save", help="Persist this chat to disk"),
    session: Optional[str] = typer.Option(None, "--session", "-s", help="Load or name a session when saving"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Provider to use (overrides defaults)"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use (overrides defaults)"),
):
    if ctx.invoked_subcommand is None:
        start_chat(save=save, session=session, provider=provider, model=model)


# -------- commands --------

@chat_app.command("start")
def start_chat(
    save: bool = typer.Option(False, "--save", help="Persist this chat to disk"),
    session: Optional[str] = typer.Option(None, "--session", "-s", help="Load or name a session when saving"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Provider to use (overrides defaults)"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use (overrides defaults)"),
):
    """
    Start an interactive chat. Saving is OFF by default; enable with --save.

    Slash commands:
      /model <id>       change model
      /provider <name>  change provider
      /save on|off      toggle saving
      /status           show current settings
      /load <name>      load an existing saved session
      /history [N]      show last N messages (default 20)
      exit|quit         leave chat
    """
    prov, mdl = resolve_provider_model(provider, model)

    # Create or load a session
    if session:
        try:
            s = ChatSession.load(session)
            # Respect requested save flag and any overrides
            s.save = bool(save)
            if provider or model:
                try:
                    s.switch(provider=provider, model=model)
                except Exception as e:
                    typer.echo(f"Failed to apply provider/model overrides: {e}")
        except FileNotFoundError:
            # New session with this name
            s = ChatSession(provider=prov, model=mdl, save=save, name=session)
    else:
        # New unnamed session (will auto-name when saving)
        s = ChatSession(provider=prov, model=mdl, save=save, name=None)

    typer.echo('Type your messages. Ctrl-D or type "exit" to quit.')
    typer.echo(f'Saving: {"ON" if s.save else "OFF"} | Provider: {s.provider} | Model: {s.model}')
    if s.save:
        typer.echo(f"Session: {s.name} (files in {_sessions_dir()})")

    while True:
        try:
            line = input("you> ").strip()
        except EOFError:
            break
        if not line:
            continue

        low = line.lower()
        if low in {"exit", "quit"}:
            break

        # Slash commands
        if line.startswith("/"):
            parts = line.split(None, 1)
            cmd = parts[0].lstrip("/")
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "model" and arg:
                try:
                    s.switch(model=arg)
                    typer.echo(f"(model set to {s.model})")
                except Exception as e:
                    typer.echo(f"Failed to switch model: {e}")
                continue

            if cmd == "provider" and arg:
                try:
                    s.switch(provider=arg)
                    typer.echo(f"(provider set to {s.provider})")
                except Exception as e:
                    typer.echo(f"Failed to switch provider: {e}")
                continue

            if cmd == "save":
                arg_low = arg.lower()
                if arg_low in {"on", "true", "1"}:
                    s.save = True
                    typer.echo("(saving is now ON; subsequent turns will be persisted)")
                elif arg_low in {"off", "false", "0"}:
                    s.save = False
                    typer.echo("(saving is now OFF)")
                else:
                    typer.echo("Usage: /save on|off")
                continue

            if cmd == "status":
                typer.echo(
                    f'Provider: {s.provider} | Model: {s.model} | Saving: {"ON" if s.save else "OFF"} | Session: {s.name or "(ephemeral)"}'
                )
                continue

            if cmd == "load" and arg:
                try:
                    s = ChatSession.load(arg)
                    typer.echo(
                        f"(loaded session {arg}; provider={s.provider}, model={s.model}, saving={'ON' if s.save else 'OFF'})"
                    )
                except FileNotFoundError:
                    typer.echo(f"No saved session named {arg!r}")
                continue

            if cmd == "history":
                try:
                    n = int(arg) if arg else 20
                except ValueError:
                    n = 20
                for m in s.messages[-n:]:
                    _print_msg(m.role, m.content, m.ts)
                continue

            typer.echo("Unknown command. Try: /model, /provider, /save, /status, /load, /history")
            continue

        # Normal chat turn
        try:
            reply = s.send(line)
            typer.echo(f"assistant> {reply}")
        except Exception as e:
            typer.echo(f"Error: {e}")

    typer.echo("Bye.")


@chat_app.command("history")
def show_history(
    session: Optional[str] = typer.Option(None, "--session", "-s", help="Saved session name (default: most recent)"),
    last: int = typer.Option(20, "--last", "-n", help="Show the last N messages"),
):
    """Show messages from a saved chat."""
    if session is None:
        saved = _list_saved_sessions()
        if not saved:
            typer.echo("No saved sessions found.")
            raise typer.Exit(code=0)
        session = saved[-1]

    try:
        s = ChatSession.load(session)
    except FileNotFoundError:
        typer.echo(f"No saved session named {session!r}")
        raise typer.Exit(code=1)

    if not s.messages:
        typer.echo("Session has no messages.")
        raise typer.Exit(code=0)

    typer.echo(
        f"Session: {s.name} | Provider: {s.provider} | Model: {s.model} | Saving: {'ON' if s.save else 'OFF'}"
    )
    for m in s.messages[-last:]:
        _print_msg(m.role, m.content, m.ts)


@chat_app.command("list")
def list_sessions():
    """List saved chat sessions."""
    saved = _list_saved_sessions()
    if not saved:
        typer.echo("No saved sessions.")
        return
    typer.echo("Saved sessions:")
    for name in saved:
        meta_path = _sessions_dir() / f"{name}.json"
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            count = len(data.get("messages", []))
            typer.echo(f"  - {name} ({count} messages)")
        except Exception:
            typer.echo(f"  - {name}")
