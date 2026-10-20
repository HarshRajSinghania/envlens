# examples/

Two files, both fake values, both committed on purpose.

| File | Why it exists |
| --- | --- |
| `.env.example` | the documented contract — what the app needs |
| `.env` | a realistic local file with two kinds of drift |

`examples/.env` is deliberately imperfect so the demo output is not a wall of `ok`:

- `API_TOKEN` is empty in `.env.example` and absent in `.env` → optional, warning
- `DEBUG_TOKEN` is set in `.env` and not documented → undocumented, warning

Run it:

```bash
python envlens.py check --example examples/.env.example --actual examples/.env
python envlens.py diff  examples/.env.example examples/.env
python envlens.py mask  examples/.env
python envlens.py docs  --example examples/.env.example
```

`diff` and `check` exit `1` on drift by design. `make demo` adds `|| true` so the
Makefile does not stop on the expected failure.
