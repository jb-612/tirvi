"""F21 (POC seed) — Hebrew homograph override lexicon.

Spec: PRD §6.4 (homograph-overrides). Issue #20.

POC seed only. The full F21 design is pending; this 5–20 entry map
captures the most-flagged modern-Hebrew picks where Nakdan's default
diverges from current usage. Each entry maps the *undecorated* surface
form to the preferred diacritized form.

Adding entries: append (undecorated, preferred-with-nikud) pairs as
they surface from human listening + the issue tracker. Don't try to
seed a thousand at once — the override is a safety-net, not a
replacement for context-aware disambiguation.
"""

HOMOGRAPH_OVERRIDES: dict[str, str] = {
    # כל → kol (modern), not kal (biblical/construct)
    # Issue #18 user feedback 2026-04-30
    "כל": "כֹּל",
}
