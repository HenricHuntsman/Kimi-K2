#!/usr/bin/env python3
"""Local Ollama chat client. No cloud fallback, downloads or tool execution."""

import argparse
import ipaddress
import json
import math
import os
import re
import sys
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class LocalModelError(Exception):
    """A configuration, transport or model response could not be verified."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise LocalModelError("Ollama redirects are disabled")


class LocalOllama:
    max_response = 2 * 1024 * 1024
    max_prompt = 128 * 1024

    def __init__(self, model="qwen2.5-coder:7b", endpoint="http://127.0.0.1:11434",
                 timeout=120):
        if (not isinstance(model, str) or not re.fullmatch(r"[A-Za-z0-9_./:-]{1,200}", model)
                or "cloud" in model.lower()):
            raise LocalModelError("Choose an installed local model, without a cloud tag")
        try:
            parts = urlsplit(endpoint)
            host = parts.hostname
            if host == "localhost":
                host = "127.0.0.1"
            if (parts.scheme != "http" or not ipaddress.ip_address(host).is_loopback
                    or parts.username is not None or parts.password is not None
                    or parts.path not in ("", "/") or parts.query or parts.fragment):
                raise ValueError()
            port = parts.port if parts.port is not None else 11434
            if not 1 <= port <= 65535:
                raise ValueError()
            timeout = float(timeout)
            if not math.isfinite(timeout) or timeout <= 0 or timeout > 600:
                raise ValueError()
        except (ValueError, TypeError):
            raise LocalModelError("Use a loopback HTTP endpoint and a timeout of 0–600 seconds") from None
        self.endpoint = f"http://{'[' + host + ']' if ':' in host else host}:{port}"
        self.model, self.timeout = model, timeout
        self.opener = build_opener(ProxyHandler({}), NoRedirect())

    @classmethod
    def from_environment(cls):
        return cls(os.environ.get("FORGE_OLLAMA_MODEL", "qwen2.5-coder:7b"),
                   os.environ.get("FORGE_OLLAMA_URL", "http://127.0.0.1:11434"),
                   os.environ.get("FORGE_OLLAMA_TIMEOUT", "120"))

    def _request(self, path, payload=None, timeout=None):
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(self.endpoint + path, data=body,
                          headers={"Content-Type": "application/json"})
        try:
            with self.opener.open(request, timeout=timeout or self.timeout) as response:
                raw = response.read(self.max_response + 1)
            if len(raw) > self.max_response:
                raise LocalModelError("Ollama response exceeded the 2 MiB limit")
            value = json.loads(raw)
        except HTTPError as error:
            raise LocalModelError(f"Ollama returned HTTP {error.code}; check server and installed model") from None
        except (URLError, TimeoutError, OSError, HTTPException):
            raise LocalModelError("Local Ollama is unavailable or timed out; no fallback was used") from None
        except (ValueError, UnicodeError):
            raise LocalModelError("Ollama returned invalid JSON") from None
        if not isinstance(value, dict) or value.get("error"):
            raise LocalModelError("Ollama returned an invalid or failed response")
        return value

    def check_local(self):
        """Fail before sending prompt text unless server confirms local-only mode."""
        status = self._request("/api/status", timeout=min(5, self.timeout))
        cloud = status.get("cloud")
        if not isinstance(cloud, dict) or cloud.get("disabled") is not True:
            raise LocalModelError("Ollama must confirm cloud disabled; start it with OLLAMA_NO_CLOUD=1")
        info = self._request("/api/show", {"model": self.model}, min(5, self.timeout))
        if info.get("remote_host") or info.get("remote_model"):
            raise LocalModelError("Remote-backed models are disabled")
        if not isinstance(info.get("model_info"), dict) or not info["model_info"]:
            raise LocalModelError("Local model metadata is missing; verify the installed model")
        return {"backend": "ollama", "model": self.model, "cloud_disabled": True,
                "inference_verified": False}

    def chat(self, messages):
        if not isinstance(messages, list) or not messages or len(messages) > 100:
            raise LocalModelError("Provide 1–100 chat messages")
        clean = []
        for message in messages:
            if (not isinstance(message, dict) or message.get("role") not in
                    ("user", "assistant", "system") or not isinstance(message.get("content"), str)
                    or not message["content"].strip()):
                raise LocalModelError("Messages need a supported role and nonempty text")
            clean.append({"role": message["role"], "content": message["content"]})
        try:
            size = sum(len(m["content"].encode("utf-8")) for m in clean)
        except UnicodeError:
            raise LocalModelError("Messages must contain valid UTF-8 text") from None
        if size > self.max_prompt:
            raise LocalModelError("Chat history exceeds 128 KiB; clear or shorten it")
        self.check_local()
        result = self._request("/api/chat", {"model": self.model, "messages": clean,
                                            "stream": False})
        message = result.get("message")
        if (result.get("done") is not True or result.get("remote_host")
                or not isinstance(result.get("model"), str)
                or not isinstance(message, dict) or message.get("role") != "assistant"
                or not isinstance(message.get("content"), str) or not message["content"].strip()
                or message.get("tool_calls")):
            raise LocalModelError("Ollama did not return a complete plain-text assistant answer")
        return {"message": message["content"], "model": result["model"],
                "backend": "ollama", "demo": False, "inference_verified": True,
                "capabilities_used": []}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", nargs="?", help="One-shot prompt; omit for interactive chat")
    parser.add_argument("--model", default=os.environ.get("FORGE_OLLAMA_MODEL", "qwen2.5-coder:7b"))
    parser.add_argument("--endpoint", default=os.environ.get("FORGE_OLLAMA_URL", "http://127.0.0.1:11434"))
    parser.add_argument("--timeout", default=os.environ.get("FORGE_OLLAMA_TIMEOUT", "120"))
    parser.add_argument("--check", action="store_true", help="Check server policy/model metadata without inference")
    args = parser.parse_args(argv)
    try:
        client = LocalOllama(args.model, args.endpoint, args.timeout)
        if args.check:
            print(json.dumps(client.check_local()))
            return 0
        if args.prompt is not None:
            print(client.chat([{"role": "user", "content": args.prompt}])["message"])
            return 0
        print(f"Local Ollama / {args.model}. /clear resets history; /exit quits. No tools execute.")
        history = []
        while True:
            prompt = input("You: ").strip()
            if prompt == "/exit":
                return 0
            if prompt == "/clear":
                history.clear()
                continue
            if not prompt:
                continue
            candidate = history + [{"role": "user", "content": prompt}]
            try:
                result = client.chat(candidate)
            except LocalModelError as error:
                print(f"Error: {error}", file=sys.stderr)
                continue
            history = candidate + [{"role": "assistant", "content": result["message"]}]
            print(f"{result['model']}: {result['message']}")
    except LocalModelError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        return 0


if __name__ == "__main__":
    sys.exit(main())
