---
name: github-issue-triage
description: 'Analyze GitHub issues linked to code changes — detect duplicates, verify PR-issue cross-references, assess resolution completeness, and suggest labels or milestones.'
---

# GitHub Issue Triage

Review GitHub issues related to a code change or Pull Request to ensure proper linkage, completeness, and prioritization.

## Process

1. **Identify related issues**:
   - Extract issue references from PR description (`Closes #N`, `Fixes #N`, `Resolves #N`)
   - Use `search_issues` to find open issues in the same area (by labels, keywords from PR title, or affected files)
   - Use `list_issues` filtered by `state=open` to surface recently active issues

2. **Fetch issue details** for each linked issue using `get_issue`:
   - Title, body, labels, assignees, milestone, created/updated dates
   - Comment thread for additional context or reproductions steps

3. **Detect duplicates and related issues**:
   - Search for issues with similar titles or keywords using `search_issues`
   - Flag issues that describe the same symptom but were filed separately
   - Suggest merging duplicates with a reference comment

4. **Verify PR-to-issue linkage**:
   - Confirm the PR description explicitly closes the linked issues
   - If issues exist for the changed area but are NOT referenced in the PR, flag them
   - Ensure the PR targets the correct base branch for the issue's target milestone

5. **Evaluate resolution completeness**:
   - Map each acceptance criterion in the issue to the actual code change
   - Flag criteria that are partially addressed or missing from the diff
   - Note if the fix is a workaround vs. a root-cause resolution

6. **Review issue metadata quality**:
   - Labels present and accurate (bug, enhancement, security, documentation, etc.)
   - Assignee set if the issue is in progress
   - Milestone assigned if the issue is part of a planned release
   - Reproduction steps present for bug reports

7. **Emit triage report**:
   - Table of linked issues with status: FULLY RESOLVED / PARTIALLY RESOLVED / UNADDRESSED
   - List of unlinked issues that may be affected by this change
   - Metadata gaps with suggested labels, milestones, or assignees
   - Duplicate candidates with suggested consolidation action

## Labels Reference (Common)

| Label          | Use for                                        |
|----------------|------------------------------------------------|
| `bug`          | Incorrect behavior confirmed                   |
| `enhancement`  | New feature or improvement request             |
| `security`     | Vulnerability or security hardening            |
| `documentation`| Docs missing or outdated                       |
| `breaking`     | Change that requires consumer updates          |
| `wontfix`      | Intentionally not addressed                    |
| `duplicate`    | Same as an existing issue                      |
