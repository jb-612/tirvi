# F43 Scaffold Notes

## Created
- `tirvi/ttl/__init__.py` — re-exports `TTLReport`, `apply_ttl`
- `tirvi/ttl/policy.py` — `TTLReport` dataclass + `apply_ttl(resource_paths, policy)` deferred stub
- `tests/unit/test_ttl_automation.py` — gate stub: imports, dataclass constructable, runner raises `NotImplementedError`

## Status
- Feature deferred post-POC per design.md. Scaffold + gate stub only.
- T-01 marker flipped to `[x]` in tasks.md.

## Notes
- Signature follows team-lead spec: `apply_ttl(resource_paths, policy) -> TTLReport`.
- Default policy (7-day TTL on `pdfs/`/`pages/`/`plans/`/`manifests/`, exclude `audio/`) carried in dataclass fields per design DE-01.

## Disputes
- tasks.md test_file: `tests/unit/test_ttl_cleanup.py`; team-lead glob `test_ttl*.py`. Used `test_ttl_automation.py` (matches feature slug). Logged in `dispute-item.md`.
