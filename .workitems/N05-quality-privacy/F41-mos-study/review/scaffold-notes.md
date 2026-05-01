# F41 Scaffold Notes

## Created
- `tirvi/mos/__init__.py` — re-exports `MOSResult`, `run_mos_study`
- `tirvi/mos/study.py` — `MOSResult` dataclass + `run_mos_study(audio_paths, config)` deferred stub
- `tests/unit/test_mos_study.py` — gate stub: imports, dataclass constructable, runner raises `NotImplementedError`

## Status
- Feature deferred post-POC per design.md. Scaffold + gate stub only.
- T-01 marker flipped to `[x]` in tasks.md.

## Notes
- Signature follows team-lead spec: `run_mos_study(audio_paths, config) -> MOSResult`.
- ITU-T P.800 5-point scale aggregation deferred to TDD pass.

## Disputes
- tasks.md test_file: `tests/unit/test_mos_aggregation.py`; team-lead spec uses `test_mos*.py` glob. Used `test_mos_study.py` to align with the public entry point name. Logged in `dispute-item.md`.
