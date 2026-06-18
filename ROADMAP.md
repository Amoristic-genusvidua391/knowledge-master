# Roadmap to v1.0.0

## v0.3.0 — Multi-language static analysis

- [ ] TypeScript/JavaScript import graph (tree-sitter)
- [ ] Go import graph (tree-sitter)
- [ ] Rust use/mod graph (tree-sitter)
- [ ] Function-level call graph (not just file imports)
- [ ] Cross-file symbol resolution ("who calls validate_token?")

## v0.4.0 — Reliability & migrations

- [ ] Schema versioning (store version in graph metadata)
- [ ] `km upgrade` command (migrate graph between versions)
- [ ] Error recovery for partial indexing (transaction/rollback)
- [ ] Deduplication (same file indexed from different paths)
- [ ] Stale data cleanup (TTL or "last seen" tracking)

## v0.5.0 — Platform & testing

- [ ] Windows CI (GitHub Actions matrix)
- [ ] Windows path handling fixes
- [ ] Battle-test on 5+ diverse repos (monorepo, microservices, frontend)
- [ ] Integration test suite (30+ tests)
- [ ] Benchmark re-ranker vs raw cosine (precision@5 on test set)
- [ ] Load test: 10k files, measure indexing time + query latency

## v0.6.0 — Advanced features

- [ ] `km safe-to-change <target>` (blast radius + test coverage = risk score)
- [ ] Cross-repo dependency resolution (pip/npm packages → linked repos)
- [ ] Scheduled sync (cron-based re-indexing)
- [ ] Change risk scoring (blast radius breadth × test gaps)
- [ ] CHANGELOG.md (auto-generated from conventional commits)

## v1.0.0 — Stable release

- [ ] Stable API (no breaking changes without major version)
- [ ] Full documentation with examples for all features
- [ ] Published to MCP registry
- [ ] Homebrew tap (`brew install knowledge-master`)
- [ ] VS Code extension (index from IDE)
- [ ] 50+ tests, >80% coverage on core modules
