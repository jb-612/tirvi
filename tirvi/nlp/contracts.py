"""F18 — NLPResult contract helper (consumed by adapters + downstream features).

Spec: N02/F18 DE-05. AC: US-01/AC-01.
"""

from tirvi.results import NLPResult


def assert_nlp_result_v1(result: NLPResult) -> None:
    """Assert that ``result`` conforms to the F18 NLPResult v1 contract.

    Invariants (named, TDD fills):
      - INV-NLP-CONTRACT-001 (DE-05): UD-Hebrew POS whitelist enforced per token
      - INV-NLP-CONTRACT-002 (DE-05): morph keys whitelisted (Number, Gender, Person, …)
      - INV-NLP-CONTRACT-003 (DE-05): ``ambiguous`` consistent with margin threshold
      - INV-NLP-CONTRACT-004 (biz S01): every ``confidence`` is float|None, never 0.0

    Raises :class:`tirvi.errors.SchemaContractError` on any contract violation.
    """
    # TODO INV-NLP-CONTRACT-001..004: validate every token against whitelist
    raise NotImplementedError
