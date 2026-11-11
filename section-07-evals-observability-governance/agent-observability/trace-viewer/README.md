# Agent trace viewer

A friendlier view of the traces in Jaeger, made for agent runs: a timeline of every step, token and time totals, and a step-by-step story (prompt → model calls → tool calls → answer).

```bash
# 1. Jaeger running (see 02_jaeger_tracing_groq.ipynb), and at least one traced agent run
# 2. Start the viewer (standard library only, no installs)
python serve.py
# 3. Open http://localhost:8090
```

The page refreshes every 10 seconds, so new runs appear while you work. Jaeger's own UI is still at http://localhost:16686.

`serve.py` exists because Jaeger's API doesn't allow pages on other ports to read it (no CORS headers). It serves `index.html` and forwards `/api/...` to Jaeger. Settings: `JAEGER_URL` (default `http://localhost:16686`) and `PORT` (default `8090`).
