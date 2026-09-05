#!/usr/bin/env python3
"""SOP draft factory. No cloud required.

Usage:
  python sop_draft.py
  python sop_draft.py --run          # try local Ollama if up
  python sop_draft.py --gold gold.md --source source.txt --out draft.md

Reads gold.md + source.txt, writes prompt.txt (always) and draft.md (if --run works).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

PROMPT = """You are a technical writer for regulated medical/clinical documentation.

Fill this exact template using ONLY facts from SOURCE below.

TEMPLATE STRUCTURE (copy from gold.md):
{gold}

RULES:
1. Preserve ALL heading levels and section order exactly.
2. For each section, extract facts ONLY from SOURCE.
3. If a required fact is missing from SOURCE, write:
   [NEED SME: <section> – <specific missing info>]
4. Do NOT invent numbers, times, setpoints, volumes, or limits.
5. Generate a revision table with today's date ({today}) and "Draft" as version.
6. Keep formatting plain text – I'll handle Word/Veeva later.

SOURCE:
{source}

OUTPUT:
- Full drafted SOP with [NEED SME] placeholders
- Revision table at top
- Definition list populated from SOURCE (flag missing terms)
"""


def read(path: str) -> str:
    if not os.path.exists(path):
        print(f"missing: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        print(f"empty: {path}", file=sys.stderr)
        sys.exit(1)
    return text


def ollama(prompt: str, model: str, host: str, timeout: int) -> str:
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        f"{host.rstrip('/')}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    return data.get("response", "").strip()


def main() -> None:
    p = argparse.ArgumentParser(description="Assemble SOP draft prompt; optional local Ollama.")
    p.add_argument("--gold", default="gold.md")
    p.add_argument("--source", default="source.txt")
    p.add_argument("--out", default="draft.md")
    p.add_argument("--prompt-out", default="prompt.txt")
    p.add_argument("--run", action="store_true", help="call local Ollama")
    p.add_argument("--model", default=os.environ.get("OLLAMA_MODEL", "llama3.2"))
    p.add_argument("--host", default=os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434"))
    p.add_argument("--timeout", type=int, default=180)
    args = p.parse_args()

    today = dt.date.today().isoformat()
    prompt = PROMPT.format(gold=read(args.gold), source=read(args.source), today=today)

    with open(args.prompt_out, "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"wrote {args.prompt_out} ({len(prompt)} chars)")

    if not args.run:
        print("paste prompt.txt into any chat. or rerun with --run if Ollama is local.")
        return

    try:
        draft = ollama(prompt, args.model, args.host, args.timeout)
    except urllib.error.URLError as e:
        print(f"ollama down: {e}. use prompt.txt instead.", file=sys.stderr)
        sys.exit(2)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(draft + "\n")
    flags = draft.count("[NEED SME")
    print(f"wrote {args.out}  NEED SME flags: {flags}")


if __name__ == "__main__":
    main()
