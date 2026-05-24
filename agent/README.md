# Wren Employee Analytics Agent

This directory contains a Pydantic AI agent that answers employee analytics
questions through Wren's semantic layer. The source database is Postgres. Wren
memory is stored in LanceDB using MinIO as the S3-compatible backend.

The agent does not query raw tables directly. It uses Wren tools generated from
the project in `db/`:

- `wren_fetch_context`
- `wren_recall_queries`
- `wren_dry_plan`
- `wren_query`
- `wren_store_query`

## Current Architecture

```text
Postgres employee_demo
  |
  v
Wren project in agent/db
  |
  | context build creates db/target/mdl.json
  v
LanceDB memory at s3://wren-lancedb/memory
  |
  | MinIO service from ../docker-compose.yml
  v
Pydantic AI agent in main.py
```

Local infrastructure is defined in the repository root `docker-compose.yml`:

- `postgres`: employee demo database on `localhost:5432`.
- `minio`: S3-compatible object storage on `localhost:9000`.
- `lancedb-bucket`: one-shot initializer for the `wren-lancedb` bucket.

MinIO console:

```text
http://localhost:9001
minioadmin / minioadmin
```

## Important Files

- `main.py`: runs the demo questions, prints an observable tool trace, final SQL,
  and final answer for each question.
- `index_memory.py`: indexes `db/target/mdl.json` into LanceDB memory.
- `wren_memory.py`: local adapter that makes `wren-pydantic` use the S3-backed
  LanceDB path instead of the SDK's default local `.wren/memory` discovery.
- `db/wren_project.yml`: Wren project definition.
- `db/profiles/employee_pg.yml`: local Postgres profile.
- `db/relationships.yml`: relationship definitions.
- `db/target/mdl.json`: generated Wren manifest consumed by the agent.

## Prerequisites

- Docker with Compose.
- `uv`.
- Python version from `.python-version`.
- An OpenAI API key in `agent/.env` or exported in the shell.

Expected `agent/.env` values:

```bash
OPENAI_API_KEY=...
WREN_MEMORY_PATH=s3://wren-lancedb/memory
AWS_ENDPOINT=http://localhost:9000
AWS_ENDPOINT_URL=http://localhost:9000
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_DEFAULT_REGION=us-east-1
ALLOW_HTTP=true
```

`wren_memory.py` sets these LanceDB/MinIO values by default for local runs, so
only `OPENAI_API_KEY` is normally required in `.env`.

## Run Locally

From the repository root:

```bash
cd /Users/rajatnigam/workspace/wren/gen_bi
docker compose up -d
```

From `agent/`:

```bash
cd agent
uv sync
uv run wren context build
uv run python index_memory.py --mdl db/target/mdl.json
uv run main.py
```

The expected flow is:

1. `wren context build` refreshes `db/target/mdl.json`.
2. `index_memory.py` writes schema memory and seed query examples to
   `s3://wren-lancedb/memory`.
3. `main.py` builds a Wren toolkit with memory enabled, asks the configured
   questions, prints tool calls/returns, prints the final `wren_query` SQL, and
   prints the final answer.

## Memory Storage Contract

The canonical memory location is:

```text
s3://wren-lancedb/memory
```

For local host execution, use:

```bash
AWS_ENDPOINT=http://localhost:9000
AWS_ENDPOINT_URL=http://localhost:9000
```

For a containerized app on the compose network, use:

```bash
AWS_ENDPOINT=http://minio:9000
AWS_ENDPOINT_URL=http://minio:9000
```

Keep `ALLOW_HTTP=true` for local MinIO because it is not using TLS.

## Operational Commands

Rebuild semantic context after changing Wren models or relationships:

```bash
uv run wren context build
```

Rebuild LanceDB memory after changing `db/target/mdl.json`:

```bash
uv run python index_memory.py --mdl db/target/mdl.json
```

Run without seed query generation:

```bash
uv run python index_memory.py --mdl db/target/mdl.json --no-seed
```

Run against an alternate LanceDB path:

```bash
uv run python index_memory.py --mdl db/target/mdl.json --path s3://other-bucket/memory
```

Validate Python syntax:

```bash
uv run python -m py_compile main.py index_memory.py wren_memory.py
```

Validate compose syntax from the repository root:

```bash
docker compose config --quiet
```

## Maintainer Notes

- `wren-pydantic` 0.2.0 only auto-detects local `db/.wren/memory`. This project
  intentionally uses `wren_memory.py` to provide an S3-backed LanceDB memory
  provider.
- Do not reintroduce the old Postgres memory mirror. Memory now lives in
  LanceDB on MinIO.
- `main.py` does not print hidden model chain-of-thought. It prints an
  observable audit trace: tool calls, summarized tool returns, final SQL, and
  final answer.
- The final SQL is the last SQL sent to `wren_query`. `wren_dry_plan` calls may
  show intermediate SQL that was validated before execution.
- `db/target/mdl.json` must be regenerated after semantic model changes.
- Re-index memory after every meaningful MDL or instruction change.

## Troubleshooting

If memory indexing cannot connect to MinIO:

```bash
docker compose ps
docker compose logs minio
```

Confirm the bucket exists in the MinIO console or rerun:

```bash
docker compose up -d lancedb-bucket
```

If the agent cannot query Postgres, confirm the demo database is up:

```bash
docker compose ps postgres
```

The local Wren profile expects:

```text
host=localhost
port=5432
database=employee_demo
user=wren
password=wren123
```

If memory tools are missing, make sure `main.py` is using `build_toolkit("./db")`
from `wren_memory.py`, not `WrenToolkit.from_project("./db")`.

If SQL generation references nonexistent fields, rebuild both context and
memory:

```bash
uv run wren context build
uv run python index_memory.py --mdl db/target/mdl.json
```

## Production Checklist

- Replace local Postgres credentials with a read-only database user.
- Use TLS and private networking for Postgres and object storage.
- Store secrets outside source control.
- Use durable object storage instead of local MinIO for production.
- Keep `WREN_MEMORY_PATH` stable across deploys so query memory is preserved.
- Add regression questions for critical analytics workflows.
- Log question, tool status, final SQL, row count, latency, and errors.
- Review `wren_store_query` usage before enabling writes in a shared production
  memory store.
