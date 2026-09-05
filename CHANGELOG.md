# Changelog

## Unreleased — numeric input hardening

- Reject NaN, infinities, missing and boolean numeric state before clamping.
- Recheck numeric state when computing RCD, including after direct mutation.
- Preserve existing finite-value clamping and signed raw-emergence semantics.
- Add 45 regression cases; the patched repository suite has 86 passing tests.

## [0.2.0] — 2026-09-05

- replaced the compensatory Field Constant composite with Rosetta 2.0 RCD;
- made Emergence a downstream, relationally qualified observation;
- required every constitutive dependency to meet the emergence corridor floor;
- classified high raw emergence with a collapsed dependency as dissonant; and
- added non-compensation and dependency-collapse tests.

This change updates implementation semantics. It does not establish empirical
validity or a universal deployment threshold.
