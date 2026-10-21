# Extract frozen CLI core into an independent Python Engine package

The extraction core previously required the CLI source tree as its import root.
This change packages 53 frozen v1.0.0 modules under `prospector_engine`, preserving
the original source commit, normalization, typed failures, partial results and
verified-only sequential batch deduplication. CLI/export/application layers are excluded.

Adds aligned public identity evidence, public neutral observer contracts, cooperative
cancellation and explicit Chromium configuration while retaining Edge defaults.
Includes src packaging, isolated wheel validation, controlled browser diagnostics,
non-root Linux image, CI workflow and per-file provenance/test migration records.

Validation: see `docs/validation-results.json` for actual Python 3.13 Windows and
Python 3.11 Linux results, build/wheel installation and Docker browser smoke.
Live Google Maps acceptance and production browser selection remain separate.
No HTTP integration, external contract changes, stable release or main merge.
