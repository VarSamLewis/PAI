from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional
from PAI.core.config import get_api_key, read_settings, DEFAULT_MODEL, DEFAULT_PROVIDER
from ..models.model_registry import ProviderRegistry

@dataclass
class Message:
    role: str                  # 'user' | 'assistant' | 'system'
    content: str
    ts: float
    provider: Optional[str] = None
    model: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> 'Message':
        return Message(
            role=d.get('role', ''),
            content=d.get('content', ''),
            ts=d.get('ts', time.time()),
            provider=d.get('provider'),
            model=d.get('model'),
        )


class ChatSession:
    """
    Owns the conversation:
      - messages (each tagged with provider/model used for that turn)
      - current provider/model and client
      - mid-chat switching
      - optional persistence when save=True
    """

    def __init__(
        self,
        provider: str,
        model: Optional[str],
        save: bool = False,
        name: Optional[str] = None,
        history_cap: int = 200,
    ):
        self.provider = (provider or read_settings().provider or DEFAULT_PROVIDER)
        self.model    = (model    or read_settings().model    or DEFAULT_MODEL)
        api_key = get_api_key(self.provider)
        self.save = save
        self.name = name or time.strftime('chat-%Y%m%d-%H%M%S')
        self.history_cap = history_cap
        self.messages: List[Message] = []
        self._client = ProviderRegistry.get_provider(self.provider, model=self.model, api_key=api_key)

    # ---- Public API ----

    def switch(self, provider: Optional[str] = None, model: Optional[str] = None) -> None:
        if provider:
            self.provider = provider
        if model is not None:
            self.model = model or DEFAULT_MODEL
        self._client = ProviderRegistry.get_provider(self.provider, model=self.model)
        self._save_if_needed()

    def send(self, prompt: str) -> str:
        self._append('user', prompt)
        reply = self._generate(prompt)
        self._append('assistant', reply)
        self._save_if_needed()
        return reply

    # ---- Persistence ----

    @classmethod
    def load(cls, name: str) -> 'ChatSession':
        path = cls._sessions_dir() / f'{name}.json'
        if not path.exists():
            raise FileNotFoundError(name)

        data = json.loads(path.read_text(encoding='utf-8'))
        sess = cls(
            provider=data.get('current_provider') or data.get('default_provider') or 'openai',
            model=data.get('current_model') or data.get('default_model'),
            save=bool(data.get('save', True)),
            name=data.get('name', name),
            history_cap=data.get('history_cap', 200),
        )
        sess.messages = [Message.from_dict(m) for m in data.get('messages', [])]

        # If no explicit current provider/model, infer from last tagged message
        if not data.get('current_provider') or not data.get('current_model'):
            for m in reversed(sess.messages):
                if m.provider or m.model:
                    if m.provider:
                        sess.provider = m.provider
                    if m.model:
                        sess.model = m.model
                    break

        sess._client = ProviderRegistry.get_provider(sess.provider, model=sess.model)
        return sess

    @staticmethod
    def list_saved() -> List[str]:
        return sorted(p.stem for p in ChatSession._sessions_dir().glob('*.json'))

    # ---- Internals ----

    def _append(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content, ts=time.time(),
                                     provider=self.provider, model=self.model))
        if len(self.messages) > self.history_cap:
            self.messages = self.messages[-self.history_cap:]

    def _generate(self, prompt: str) -> str:
        out = self._client.generate(prompt)
        if isinstance(out, dict) and 'content' in out:
            return str(out['content'])
        return str(out)

    def _save_if_needed(self) -> None:
        if not self.save:
            return
        payload = {
            'name': self.name,
            'save': self.save,
            'created_at': self.messages[0].ts if self.messages else time.time(),
            'last_used_at': time.time(),
            'history_cap': self.history_cap,
            'current_provider': self.provider,
            'current_model': self.model,
            'messages': [m.to_dict() for m in self.messages],
        }
        path = self._sessions_dir() / f'{self.name}.json'
        tmp = path.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        os.replace(tmp, path)

    @staticmethod
    def _sessions_dir() -> Path:
        base = Path(os.environ.get('PAI_HOME') or (Path.home() / '.pai'))
        p = base / 'sessions'
        p.mkdir(parents=True, exist_ok=True)
        return p
