# Known gaps

Snapshot of 2026-11-16. Verify against code before trusting an item: it may already be fixed.
Fixed an item — delete its line in the same commit. Found a new defect — add a line here, not in
`AGENTS.md`.

openapi.yaml is out of sync with the implemented API: it uses UUID ids and envelopes
`{items, next_cursor}`, while code uses integer ids and currently returns plain arrays for
these endpoints. Fix openapi.yaml as a separate documentation change.
