"""Schema versioning and migrations for the knowledge graph."""

CURRENT_SCHEMA_VERSION = 4  # v0.4.0

# Migration definitions: version -> function that upgrades from previous version
MIGRATIONS = {}


def get_schema_version(graph) -> int:
    """Get current schema version from graph metadata."""
    try:
        result = graph.query("MATCH (m:_Meta {key: 'schema_version'}) RETURN m.value")
        if result.result_set:
            return int(result.result_set[0][0])
    except Exception:
        pass
    return 0  # no version = legacy graph


def set_schema_version(graph, version: int):
    """Store schema version in graph metadata."""
    graph.query(
        "MERGE (m:_Meta {key: 'schema_version'}) SET m.value = $version",
        params={"version": version},
    )


def check_and_migrate(graph, auto_migrate: bool = True) -> dict:
    """Check schema version and migrate if needed.

    Returns: {"current": int, "target": int, "migrated": bool, "steps": list}
    """
    current = get_schema_version(graph)
    target = CURRENT_SCHEMA_VERSION

    if current == target:
        return {"current": current, "target": target, "migrated": False, "steps": []}

    if current > target:
        raise RuntimeError(
            f"Graph schema v{current} is newer than this version supports (v{target}). "
            "Please upgrade knowledge-master."
        )

    if not auto_migrate:
        raise RuntimeError(
            f"Graph schema v{current} needs migration to v{target}. Run: km upgrade"
        )

    steps = []
    for v in range(current + 1, target + 1):
        migration_fn = MIGRATIONS.get(v)
        if migration_fn:
            migration_fn(graph)
            steps.append(f"v{v-1} → v{v}: {migration_fn.__doc__ or 'applied'}")
        else:
            steps.append(f"v{v-1} → v{v}: no-op (compatible)")

    set_schema_version(graph, target)
    return {"current": current, "target": target, "migrated": True, "steps": steps}


# --- Migrations ---

def _migrate_to_v1(graph):
    """Add indexed_at timestamp to existing chunks missing it."""
    graph.query("MATCH (c:Chunk) WHERE c.indexed_at IS NULL SET c.indexed_at = timestamp()")


def _migrate_to_v2(graph):
    """Add OWNS relationships from ownership extraction."""
    pass  # OWNS edges are created by extract_ownership, no schema change needed


def _migrate_to_v3(graph):
    """Add lang property to IMPORTS edges and Function nodes."""
    graph.query("MATCH (f:Function) WHERE f.lang IS NULL SET f.lang = 'python'")
    graph.query("MATCH ()-[e:IMPORTS]->() WHERE e.lang IS NULL SET e.lang = 'python'")


def _migrate_to_v4(graph):
    """Add content_hash to Chunk nodes for deduplication."""
    pass  # New chunks will have hash, old ones are fine without


MIGRATIONS[1] = _migrate_to_v1
MIGRATIONS[2] = _migrate_to_v2
MIGRATIONS[3] = _migrate_to_v3
MIGRATIONS[4] = _migrate_to_v4
