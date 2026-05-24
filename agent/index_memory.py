from __future__ import annotations

import argparse
import json
from pathlib import Path

from wren.context import load_instructions

from wren_memory import (
    LanceDBMemoryStore,
    configure_lancedb_storage,
    wren_memory_path,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Index Wren memory into LanceDB.")
    parser.add_argument("--mdl", default="db/target/mdl.json")
    parser.add_argument("--path", default=None)
    parser.add_argument("--no-instructions", action="store_true")
    parser.add_argument("--no-seed", action="store_true")
    args = parser.parse_args()

    configure_lancedb_storage()
    mdl_path = Path(args.mdl)
    manifest = json.loads(mdl_path.read_text())

    if not args.no_instructions:
        instructions = load_instructions(mdl_path.parent.parent)
        if instructions:
            manifest["_instructions"] = instructions

    memory_path = args.path or wren_memory_path()
    result = LanceDBMemoryStore(path=memory_path).index_schema(
        manifest,
        seed_queries=not args.no_seed,
    )
    print(
        f"Indexed {result['schema_items']} schema items"
        + (f", {result['seed_queries']} seed queries" if result["seed_queries"] else "")
        + f" at {memory_path}.",
        flush=True,
    )


if __name__ == "__main__":
    main()
