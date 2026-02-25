# AGENTS.md

## Cursor Cloud specific instructions

### Architecture overview
WellSync is a 3-service app: PostgreSQL (pgvector), FastAPI backend (port 8000), React/Vite frontend (port 5173). See `CLAUDE.md` for full tech stack.

### Starting services

1. **PostgreSQL**: `sudo docker compose up -d db` (from repo root). Uses `pgvector/pgvector:pg16` image, credentials in `.env.example`.
2. **Backend**: `python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload` (from repo root).
3. **Frontend**: `npm run dev` (from `frontend/`).

### Gotchas

- Docker must be started manually: `sudo dockerd &>/tmp/dockerd.log &` — wait ~3s before using docker commands.
- The VM runs Docker-in-Docker with `fuse-overlayfs` storage driver and `iptables-legacy`. These are configured at `/etc/docker/daemon.json`.
- Python packages install to `~/.local/bin` (user install). Ensure `$HOME/.local/bin` is on `PATH`.
- Use `python3` not `python` — only `python3` is available system-wide.
- The Vite proxy forwards `/api/*` to `http://localhost:8000/api/*` without rewrite. Backend routes include the `/api` prefix. Do NOT add a rewrite rule that strips `/api`.
- Create `.env` from `.env.example` before running the backend. The `ANTHROPIC_API_KEY` is optional for basic functionality but required for AI recommendation features.
- After starting PostgreSQL, run `python3 -m backend.create_tables` once to initialize the schema.
- `passlib[bcrypt]` is incompatible with `bcrypt>=5.0`. The code uses `bcrypt` directly instead of passlib's CryptContext.
- JWT `sub` claim MUST be a string (not int). Always use `str(user.id)` when encoding and `int(sub)` when decoding.

### Running tests

```bash
python3 -m pytest backend/tests/ -v
```

### Lint

No dedicated lint configuration exists yet. Backend follows PEP 8. For quick checks:

```bash
python3 -m py_compile backend/main.py
```

### Codebase state

MVP is functional: auth (register/login/JWT), CRUD (checkins/workouts/meals), dashboard with Chart.js trends. Agents and ML modules remain stubs awaiting implementation.
