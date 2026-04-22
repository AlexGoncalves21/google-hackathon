---
name: review-pr-changes
description: 'Structured Pull Request review — granular inline code feedback, diff analysis, test coverage, and documentation verification with a scored summary.'
---

# Review PR Changes

Perform a thorough, granular review of a Pull Request. A complete review MUST consist of specific inline feedback on code changes plus a high-level summary.

## Process

1. **Fetch PR metadata** using `get_pull_request` to obtain title, description, and context.

2. **List modified files** using `list_pull_request_files`.

3. **Granular Diff Analysis (Line-by-Line)**:
   - Use `get_pull_request_diff` for each significant file.
   - **Crucial Task**: Identify specific lines where code could be improved, contains bugs, lacks error handling, or violates project standards.
   - For every finding, note the **file path**, the **line number** (from the new version of the code), and the **reason** for the change request.

4. **Evaluate test coverage & documentation**:
   - Verify that new logic has corresponding tests.
   - Check if README or docstrings need updates.

5. **Execute Inline Feedback (Mandatory if changes are needed)**:
   - If you identified ANY issues in step 3, you **MUST** use the **Pending Review Flow** below.
   - Do NOT just list issues in the final summary; place them as comments on the actual code lines using `add_pull_request_review_comment_to_pending_review`.

6. **Emit high-level review summary**:
   - Provide an overall score: APPROVE / REQUEST CHANGES / COMMENT.
   - Summarize the main themes of your review (e.g., "Good logic but needs better error handling in the API layer").
   - Include category scores (1-5) for Logic, Tests, Docs, and Compatibility.

## Pending Review Flow

Use this flow whenever you need to add one or more inline comments. This groups all your feedback into a single notification for the developer.

1. **Initialize**: Call `create_pending_pull_request_review`. Note the `id` of the created review.
2. **Comment**: For each finding from step 3, call `add_pull_request_review_comment_to_pending_review` with the `reviewId`, `path`, `line`, and a clear, actionable `body`.
3. **Finalize**: Use `submit_pull_request_review` (or `pull_request_review_write`) to submit all pending comments along with your high-level summary and final decision (e.g., `REQUEST_CHANGES`).

## Best Practices

- **Actionable Comments**: Don't just say "this is bad". Say "This could fail if X is null; consider adding a guard clause".
- **Context**: Use the `documentation_specialist` (if available) to verify if the code follows internal architecture standards before asking for a refactor.
- **Granularity**: Prefer multiple specific inline comments over one giant wall of text in the general comment.
- **Positive Reinforcement**: Acknowledge particularly well-written or clever solutions.
