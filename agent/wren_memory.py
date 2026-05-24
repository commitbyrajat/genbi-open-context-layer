from __future__ import annotations

import os
from pathlib import Path

from wren.memory.embeddings import _DEFAULT_MODEL, get_embedding_function, warm_up
from wren.memory.store import MemoryStore
from wren_pydantic import WrenToolkit
from wren_pydantic._providers.connection import ProfileConnectionProvider
from wren_pydantic._providers.mdl_source import ProjectMDLSource
from wren_pydantic.exceptions import WrenToolkitInitError


DEFAULT_WREN_MEMORY_PATH = "s3://wren-lancedb/memory"


def wren_memory_path() -> str:
    return os.getenv("WREN_MEMORY_PATH", DEFAULT_WREN_MEMORY_PATH)


def configure_lancedb_storage() -> None:
    os.environ.setdefault("WREN_MEMORY_PATH", DEFAULT_WREN_MEMORY_PATH)
    os.environ.setdefault("AWS_ACCESS_KEY_ID", "minioadmin")
    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "minioadmin")
    os.environ.setdefault("AWS_REGION", "us-east-1")
    os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
    os.environ.setdefault("AWS_ENDPOINT", "http://localhost:9000")
    os.environ.setdefault("AWS_ENDPOINT_URL", os.environ["AWS_ENDPOINT"])
    os.environ.setdefault("ALLOW_HTTP", "true")


class LanceDBMemoryStore(MemoryStore):
    def __init__(self, path: str | Path | None = None, model_name: str | None = None):
        import lancedb

        configure_lancedb_storage()
        self._path = str(path or wren_memory_path())
        self._db = lancedb.connect(self._path)
        self._embed_fn = get_embedding_function(model_name or _DEFAULT_MODEL)
        self._dim = warm_up(self._embed_fn)


class LanceDBMemoryProvider:
    enabled = True

    def __init__(self, memory_path: str):
        self._memory_path = memory_path

    def open(self) -> LanceDBMemoryStore:
        return LanceDBMemoryStore(path=self._memory_path)


def build_toolkit(
    project: str | Path = "./db",
    *,
    profile: str | None = None,
) -> WrenToolkit:
    configure_lancedb_storage()
    project_path = Path(project).expanduser().resolve()

    if not (project_path / "wren_project.yml").exists():
        raise WrenToolkitInitError(f"wren_project.yml not found at {project_path}.")
    if not (project_path / "target" / "mdl.json").exists():
        raise WrenToolkitInitError(
            f"target/mdl.json not found at {project_path}/target/mdl.json. "
            "Run `wren context build` first."
        )

    WrenToolkit._load_project_dotenv(project_path)
    return WrenToolkit(
        project_path=project_path,
        mdl_source=ProjectMDLSource(project_path=project_path),
        connection_provider=ProfileConnectionProvider(
            project_path=project_path,
            explicit_profile=profile,
        ),
        memory_provider=LanceDBMemoryProvider(wren_memory_path()),
    )
