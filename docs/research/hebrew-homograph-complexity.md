---
tier: 5
version: 1.0
created: 2026-05-01
updated: 2026-05-01
status: current
---

# Hebrew Homograph Complexity — Design Rationale and Test-Case Seeds

## Purpose

Documents linguistic examples of Hebrew homographs that are structurally ambiguous without
vocalization (nikud). These examples are intended as:

1. **Design rationale** for why context-sensitive homograph resolution is non-trivial in
   TTS disambiguation (N02/F21 and beyond).
2. **Test-case seeds** for future homograph disambiguation tests.

See also: `data/homograph-lexicon.yaml` (current seed lexicon), `docs/PRD.md §6.4`,
N02/F21 DE-04.

---

## Examples

### 1. האם — ha-em (the mother) vs. ha-aim (whether/if)

| Reading | Transliteration | Analysis | English |
|---------|-----------------|----------|---------|
| ה + אם | ha-em | definite article ה + noun אם (mother) | "the mother" |
| האם | ha-aim | interrogative particle | "whether / if" |

**Sentence pair:**

| Hebrew | Reading | Translation |
|--------|---------|-------------|
| האם הקריאה ספר לילדה | ha-em hikriʾa sefer la-yalda | "Did **the mother** read a book to the girl?" |
| האם כדאי להקריא ספר? | ha-aim kadaʾi lehakria sefer? | "**Is it worthwhile** to read a book?" |

**Disambiguation signal:** Syntactic position. The interrogative האם occupies a clause-initial
position before a verb phrase; the definite-article construction ה+אם always introduces a
noun phrase. A POS tagger or dependency parse resolves this reliably.

**Lexicon status:** ⚠ MISSING from `data/homograph-lexicon.yaml`. Both readings must be
represented with `pos_filter` gating (NOUN vs. PART).

---

### 2. האים — ha-aim (whether, full spelling) vs. ha-e-im (the islands, short spelling)

| Reading | Transliteration | Analysis | English |
|---------|-----------------|----------|---------|
| האים | ha-aim | full-spelling variant of interrogative האם — yod marks the Hirik E vowel | "whether" (uncommon but valid) |
| האים | ha-e-im | short spelling of האיים (ha-e-yim) — ה + plural of אי (island) | "the islands" |

**Key constraint:** The definite article ה cannot prefix a verb. Therefore a reading such
as "הא-יים" (the threatened — from the verb איים) is syntactically impossible. Context
(whether the following word is a noun phrase or a predicate) disambiguates.

**Disambiguation signal:** Part-of-speech of the following constituent. Noun phrase → "the
islands"; verb phrase clause → "whether".

**Lexicon status:** ⚠ MISSING from `data/homograph-lexicon.yaml`. Both surface forms share
the same unvocalized string; disambiguation requires POS context not captured by the current
flat dict.

---

### 3. איים — e-yem (threatened, past-tense verb) vs. ayim (islands)

| Reading | Transliteration | Analysis | English |
|---------|-----------------|----------|---------|
| איים | e-yem | past tense of the verb איים (to threaten) | "threatened" |
| איים | ayim | plural of אי (island) | "islands" |

**Disambiguation signal:** Verbal vs. nominal context. A subject + איים + object pattern
points to the verb; a construct chain or definite-article attachment points to the noun.

**Lexicon status:** ⚠ MISSING. Verb form is not representable in the current
`pos_filter: null` POC schema — this is a planned gap in F21.

---

### 4. לילדה — la-yalda (to the girl, generic) vs. le-yalda (to her child, possessive)

| Reading | Transliteration | Analysis | English |
|---------|-----------------|----------|---------|
| ל + ה + ילד + ה | la-yalda | ל (to) + ה (the) + ילד (child/boy) + ה (feminine suffix) | "to **the** girl" (generic, definite) |
| ל + ילד + ה | le-yalda | ל (to) + ילדה (her child — possessive/pronominal form of ילד) | "to **her** child" (specific ownership) |

**Sentence set:**

| Hebrew | Reading | Translation |
|--------|---------|-------------|
| האם הקריאה ספר לילדה | la-yalda | "The mother read a book to **the girl**" |
| המשחק הזה מתאים לכל ילד או ילדה | la-yalda | "This game suits every boy or **girl**" |
| כל אם רוצה את הטוב ביותר לילדה | le-yalda | "Every mother wants what's best for **her child**" |

**Disambiguation signal:** Discourse coreference. The possessive reading le-yalda requires
an antecedent referent (whose child?); the generic reading la-yalda stands independently.
This is harder to resolve from surface features alone — requires coreference resolution or
pragmatic context.

**Lexicon status:** ⚠ MISSING. The two pronunciations differ in vowels that only nikud
makes explicit: "לַיַּלְדָּה" (to the girl) vs. "לְיַלְדָּה" (to her child).

---

## Prefix Letters: ב כ ל מ ה ו

Hebrew has six single-letter prefixes that attach to words:

| Prefix | Name | Meaning |
|--------|------|---------|
| ב | bet | in / at / with |
| כ | kaf | like / as |
| ל | lamed | to / for |
| מ | mem | from |
| ה | he | the (definite article) |
| ו | vav | and |

These prefixes **overlap with standalone words** that are spelled identically but mean
something different. This compounds the homograph problem beyond nikud alone:

- **ו** as a prefix = "and"; as a standalone form it can appear in biblical names
- **ה** as a prefix = "the"; the identical letter introduces a question in biblical Hebrew
- **ל** as a prefix = "to/for"; the standalone word לֹא (lo) = "no/not" can be confused
  without vowels
- **מ** as a prefix shortens the preposition מִן (from); the identical form can appear as
  part of a root (e.g., in מַה = "what")

**Design implication:** Prefix segmentation (from the YAP/HebPipe morphological analysis
layer) must precede homograph resolution. Without segmenting the prefix, the classifier
sees a longer surface form that may not appear in the lexicon at all.

---

## Design Implications for TTS Disambiguation

1. **Flat vocalization lexicon is insufficient.** The current `data/homograph-lexicon.yaml`
   schema (`surface_form → vocalized_form` with optional `pos_filter`) can handle
   simple POS-gated cases but cannot represent:
   - Two noun readings of the same surface form (האים)
   - Possessive vs. generic distinctions (לילדה)
   - Verb/noun disambiguation within a pos_filter string

2. **Morphological segmentation is a prerequisite.** Prefix stripping must run before
   any lexicon lookup. YAP/HebPipe (N02) provides this; F21 must consume segmented tokens,
   not raw surface forms.

3. **Coreference resolution is deferred but required for full accuracy.** The לילדה
   possessive case requires cross-sentence context. This is out of scope for the F21 POC
   but should be flagged as a future work item.

4. **Interrogative particles need their own tag.** האם (whether) is a special clause-initial
   particle that a general homograph table is unlikely to handle without a dedicated rule
   or dedicated `pos_filter: PART` entry. YAP assigns `PART` to this form; the lexicon
   schema can represent it once F21 POS-gated loading is enabled.

5. **POC scope is limited but correct.** The current `pos_filter: null` POC only emits
   entries with no POS restriction (כל → כֹּל). That is correct for the POC. F21 full
   implementation must enable POS-gated dispatch.

---

## Disambiguation Signals — Summary

| Example | Primary Signal | Tooling Required |
|---------|----------------|-----------------|
| האם (mother vs. whether) | Syntactic position (NP-initial vs. clause-initial) | POS tagger / dependency parser |
| האים (whether vs. islands) | POS of following constituent | POS tagger |
| איים (threatened vs. islands) | Verbal vs. nominal context | POS tagger |
| לילדה (to the girl vs. to her child) | Discourse coreference / antecedent | Coreference resolver (deferred) |
| Prefix letters (ב כ ל מ ה ו) | Morphological segmentation | YAP/HebPipe prefix segmenter |

---

## Lexicon Gap Summary

The following surface forms are NOT currently in `data/homograph-lexicon.yaml` and should
be added when F21 POS-gated loading ships:

| Surface Form | Reading A | Reading B | POS Gate Needed |
|---|---|---|---|
| האם | ha-em (the mother) | ha-aim (whether) | NOUN vs. PART |
| האים | ha-e-im (the islands) | ha-aim (whether, full) | NOUN vs. PART |
| איים | e-yem (threatened) | ayim (islands) | VERB vs. NOUN |
| לילדה | la-yalda (to the girl) | le-yalda (to her child) | Both NOUN, vowel-only diff |

---

## References

- `data/homograph-lexicon.yaml` — current POC seed lexicon (2 entries)
- N02/F21 DE-04 — homograph lexicon design element
- `docs/PRD.md §6.4` — product requirement for TTS homograph handling
- YAP/HebPipe morphological analyzer — prefix segmentation and POS tagging upstream
