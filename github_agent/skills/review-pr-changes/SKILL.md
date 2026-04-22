---
name: review-pr-changes
description: 'Structured Pull Request review — diff analysis, test coverage, documentation, and backward compatibility verification with a scored summary.'
---

# Review PR Changes

Perform a thorough, structured review of a Pull Request targeting the current repository.

## Process

1. **Fetch PR metadata** using `get_pull_request` to obtain title, description, base/head branches, and linked issues.

2. **List modified files** using `list_pull_request_files` to categorize changes by type:
   - Source code (logic, features, bug fixes)
   - Tests (unit, integration, e2e)
   - Documentation (README, docstrings, guides)
   - Configuration (env, CI/CD, dependencies)

3. **Analyze the diff** using `get_pull_request_diff` for each significant file:
   - Identify added, removed, and modified logic
   - Detect changes to public interfaces or APIs
   - Note any TODO/FIXME/HACK comments introduced

4. **Evaluate test coverage**:
   - Confirm that every new function or changed behavior has a corresponding test
   - Flag missing test cases for edge conditions
   - Check that existing tests were not removed without justification

5. **Verify documentation**:
   - Ensure new parameters, return types, and behaviors are documented
   - Confirm README or guide updates if user-facing behavior changed

6. **Check backward compatibility**:
   - Identify renamed or removed public symbols, endpoints, or config keys
   - Flag breaking changes that require a major version bump or migration guide

7. **Emit review summary** with:
   - Overall score: APPROVE / REQUEST CHANGES / COMMENT
   - Category scores (Logic, Tests, Docs, Compatibility) rated 1-5
   - Numbered list of required changes (blocking)
   - Numbered list of suggestions (non-blocking)

## Pending Review Flow

When performing detailed reviews with multiple inline comments, use the pending review tools to avoid sending multiple notifications:

1. **Start the review**:
   - Use `create_pending_pull_request_review` to initialize a review session.
   - Note the `id` of the created review.

2. **Add inline comments**:
   - Use `add_pull_request_review_comment_to_pending_review` for each finding.
   - Provide the `reviewId`, `path`, `line`, and `body` for the comment.

3. **Submit the review**:
   - Once all comments are added, use `submit_pull_request_review` (if available) or `pull_request_review_write` with the final summary to transition the review from `PENDING` to its final state.

## Best Practices

- Focus on *why* a change was made, not just *what* changed
- Prefer asking clarifying questions over assuming intent
- Distinguish blocking issues from style preferences
- Keep feedback actionable: reference file, line, and proposed fix
- Acknowledge well-written code and good test coverage explicitly
