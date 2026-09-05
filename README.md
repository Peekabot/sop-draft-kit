# sop-draft-kit

15-minute regulated SOP draft factory. Stdlib only. No cloud API.

## Run

```
python sop_draft.py
```

Writes `prompt.txt`. Paste into any chat.

```
python sop_draft.py --run
```

Calls local Ollama if it is up (`llama3.2` default).

```
python sop_draft.py --gold gold.md --source source.txt --out draft.md
```

## Loop

1. Replace `gold.md` with a real passed SOP.
2. Dump notes into `source.txt`.
3. Run.
4. Resolve only `[NEED SME]` lines. Do not let the model invent setpoints.

Human approve in Word / Confluence / Veeva is still required.
