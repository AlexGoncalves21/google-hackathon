---
name: conventional-commits
description: 'Generate and validate git commit messages following the Conventional Commits specification — infer type and scope from the diff, handle breaking changes, and enforce format rules.'
---

# Conventional Commits

Create well-formed commit messages following the [Conventional Commits 1.0.0](https://www.conventionalcommits.org/) specification, derived from actual code changes.

## Commit Format

```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

## Commit Types

| Type       | When to use                                              |
|------------|----------------------------------------------------------|
| `feat`     | New feature visible to users or API consumers            |
| `fix`      | Bug fix                                                  |
| `docs`     | Documentation only (README, docstrings, guides)          |
| `style`    | Formatting, whitespace — no logic change                 |
| `refactor` | Code restructure without behavior change                 |
| `perf`     | Performance improvement                                  |
| `test`     | Adding or correcting tests                               |
| `build`    | Build system or dependency changes                       |
| `ci`       | CI/CD pipeline configuration                             |
| `chore`    | Maintenance tasks that don't fit other types             |
| `revert`   | Reverts a previous commit                                |

## Process

1. **Analyze staged changes**:
   - Run `git diff --staged` to inspect what will be committed
   - If nothing is staged, run `git diff` to see unstaged changes and stage relevant files with `git add`

2. **Infer type and scope**:
   - Match the nature of the diff to the type table above
   - Scope = the module, package, or component primarily changed (e.g., `auth`, `agent`, `mcp`, `ci`)
   - If changes span multiple unrelated areas, consider splitting into separate commits

3. **Detect breaking changes**:
   - Look for removed or renamed public functions, classes, or config keys
   - Look for changed function signatures or API response shapes
   - If breaking: append `!` after type/scope (`feat(api)!:`) AND add footer `BREAKING CHANGE: <explanation>`

4. **Write the description**:
   - Imperative present tense: "add", "fix", "remove" — not "added", "fixes", "removed"
   - Maximum 72 characters
   - No period at the end
   - Lowercase first letter (after the colon space)

5. **Add body if needed**:
   - Explain *why* the change was made, not *what* (the diff shows what)
   - Wrap at 72 characters
   - Separate from subject with a blank line

6. **Add footers if applicable**:
   - `BREAKING CHANGE: <description>` for breaking changes
   - `Closes #N` / `Fixes #N` to link issues
   - `Co-authored-by: Name <email>` for pair commits

7. **Execute the commit**:
   ```bash
   git commit -m "$(cat <<'EOF'
   type(scope): description

   Optional body here.

   Optional footer here.
   EOF
   )"
   ```

## Examples

```
feat(mcp): add list_pull_request_files tool to github agent

fix(auth): prevent token exposure in telemetry traces

docs(readme): update local setup instructions for uv sync

refactor(agent): extract stub mode into separate function

feat(api)!: rename search_github_events skill to review_pr_changes

BREAKING CHANGE: clients referencing the old skill id must update their agent card lookup.
```

## Git Safety Rules

- Never modify git config
- Never skip hooks (`--no-verify`) unless explicitly requested
- Never force-push to `main` or `master`
- Prefer `git add <specific-files>` over `git add .` to avoid committing secrets
- Check `.env` and credential files are gitignored before staging
