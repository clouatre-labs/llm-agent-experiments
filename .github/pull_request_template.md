## Summary

<!-- What does this PR add or change? -->

## Pre-registration Checklist (experiment PRs only)

- [ ] Protocol locked before any delegates were spawned
- [ ] label-map.json sealed before run 1 (timestamps verify this)
- [ ] Rubric written and locked before run 1
- [ ] All JSON data files validate with `jq empty`
- [ ] Session counts match protocol (verify with `ls experiments/*/sessions/ | wc -l`)
- [ ] No raw/ conversation logs committed (document gap in README if applicable)

## Data Integrity

- [ ] All `.json` files parse cleanly: `for f in experiments/**/*.json; do jq empty "$f" && echo "ok: $f"; done`
- [ ] Session file naming follows `scout-run-NN.json` convention (2-digit zero-padded)

## Commit

- [ ] GPG signed: `git log --show-signature -1`
- [ ] DCO sign-off: `Signed-off-by:` present in commit message
