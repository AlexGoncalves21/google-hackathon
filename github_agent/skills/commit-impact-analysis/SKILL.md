---
name: commit-impact-analysis
description: 'Analyze the commit history of a Pull Request to detect breaking changes, regression risk, message quality issues, and atomicity problems — with recommendations for squash or rebase.'
---

# Commit Impact Analysis

Analyze the individual commits in a Pull Request to assess risk, message quality, and whether they are structured for a clean merge.

## Process

1. **List all commits in the PR**:
   - Use `list_pull_request_commits` (GitHub MCP) or `git log <base>..<head> --oneline` to get the full commit list
   - Note: analyze ALL commits, not just the latest one

2. **Evaluate message quality** for each commit:
   - Does the subject line clearly explain the change?
   - Is it in imperative present tense? (e.g., "add X" not "added X")
   - Does it follow Conventional Commits format? (see `conventional-commits` skill)
   - Are there WIP, temp, fixup, or squash-me markers that signal unfinished cleanup?

3. **Assess atomicity** — each commit should represent one logical change:
   - Flag commits that mix unrelated changes (e.g., feature + unrelated refactor)
   - Flag commits that partially implement a feature across multiple commits without bisect-safety
   - Flag fixup commits that correct a mistake in a prior commit in the same PR

4. **Detect breaking changes** in the commit history:
   - Look for removed or renamed public symbols, config keys, or endpoints in diffs
   - Check if BREAKING CHANGE footer is present when the diff indicates it's needed
   - Identify migration path if breaking change exists

5. **Estimate regression risk**:
   - Commits touching core logic, auth, database schemas, or public APIs carry HIGH risk
   - Commits touching tests only or docs only carry LOW risk
   - Commits modifying CI/CD or deployment config carry MEDIUM risk
   - Flag if high-risk commits lack corresponding test additions

6. **Check for sensitive content** in commit history:
   - Secrets or credentials ever committed (even if later removed — they persist in git history)
   - Large binary files added and then removed
   - Accidental inclusion of `.env`, credentials files, or private keys

7. **Emit impact report**:
   - Commit-by-commit table: `| SHA | Message | Risk | Issues |`
   - Breaking changes section with affected interface and recommended migration
   - Atomicity recommendations: commits to squash, reorder, or split
   - Overall merge readiness: CLEAN / NEEDS CLEANUP / NEEDS REBASE

## Risk Reference

| Risk Level | Typical Change Type                                      |
|------------|----------------------------------------------------------|
| CRITICAL   | Secrets committed, data loss risk                        |
| HIGH       | Breaking API/config change, auth logic modified          |
| MEDIUM     | Core business logic, DB schema, CI/CD pipeline           |
| LOW        | Tests, docs, style, minor refactors                      |
| NEGLIGIBLE | README typo, comment update                              |

## Recommendations

- **Squash** when: PR has fixup commits, WIP markers, or many small "oops" commits
- **Rebase** when: commits are out of logical order or based on a stale branch
- **Split** when: a single commit contains unrelated changes that should be reverted independently
- **Keep as-is** when: each commit is atomic, well-named, and bisect-safe
