from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from openai import OpenAI

from .model_registry import ProviderRegistry
from . import systemprompt


@ProviderRegistry.register("openai")
class OpenAIClient:
    """
    Thin adapter around the OpenAI Chat Completions API.

    Usage patterns:
      - One-shot:  generate(prompt="Hello")
      - With history: generate(messages=[{"role":"system","content":"..."},{"role":"user","content":"Hi"}, ...])

    Notes:
      - If you pass `messages`, they are used verbatim (no system prompt is injected).
      - If you pass only `prompt`, a default system prompt is prepended.
      - You can override model per-call via generate(..., model="gpt-4o-mini").
    """

    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        **_: Any,
    ):
        # Resolve API key: prefer explicit param, then env var.
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Missing OpenAI API key. Set the OPENAI_API_KEY environment variable "
                "or pass api_key= when constructing the provider."
            )

        self.model = model or self.DEFAULT_MODEL
        # Allow custom base_url for proxies / self-hosted gateways (optional)
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)

    def generate(self, prompt: Optional[str] = None, **kwargs: Any) -> str:
        """
        Return a single string completion.

        Parameters (kwargs are passed through to OpenAI):
          - messages: Optional[List[Dict[str, str]]]
              If provided, used verbatim. Otherwise, a simple [system, user] list is built from `prompt`.
          - model: Optional[str]
              Overrides the instance model for this call.
          - temperature, max_tokens, etc.: forwarded to the SDK.

        Streaming is not handled here; this method returns the full text.
        """
        # Allow callers to pass a full messages list. If absent, build it from `prompt`.
        messages: Optional[List[Dict[str, str]]] = kwargs.pop("messages", None)
        call_model: str = kwargs.pop("model", self.model)

        if messages is None:
            if prompt is None or not str(prompt).strip():
                raise ValueError("Prompt cannot be empty")
            sys_content = systemprompt.system_prompt
            messages = [
                {"role": "system", "content": sys_content},
                {"role": "user", "content": prompt},
            ]

        params: Dict[str, Any] = {
            "model": call_model,
            "messages": messages,
        }
        params.update(kwargs)

        resp = self.client.chat.completions.create(**params)
        # Defensive: handle empty choices gracefully
        if not getattr(resp, "choices", None):
            return ""
        return (resp.choices[0].message.content or "").strip()

    def models(self) -> list[str]:
        return sorted([m.id for m in self.client.models.list().data])
