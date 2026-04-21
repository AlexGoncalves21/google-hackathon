---
name: security-change-review
description: 'Security-focused review of code changes — OWASP Top 10, secret exposure, authentication/authorization, input validation, and dependency risks.'
---

# Security Change Review

Perform a security-focused analysis of a Pull Request or set of code changes, mapping findings to severity levels.

## Process

1. **Scan for exposed secrets** in the diff:
   - Hardcoded API keys, tokens, passwords, connection strings
   - Credentials in config files, test fixtures, or comments
   - Patterns: `token=`, `password=`, `secret=`, `api_key=`, `-----BEGIN`
   - **Severity: CRITICAL** — block merge immediately

2. **Review authentication and authorization changes**:
   - New or modified auth middleware, decorators, guards
   - Changes to permission checks, role validation, or ACL logic
   - Ensure `@login_required`, JWT validation, or equivalent is not removed
   - **Severity: HIGH** if protection is weakened or removed

3. **Check for injection vulnerabilities** (OWASP A03):
   - SQL: raw string concatenation in queries instead of parameterized statements
   - Command injection: `subprocess`, `os.system`, `exec` with unsanitized input
   - XSS: unescaped user content rendered in HTML templates
   - **Severity: HIGH / CRITICAL** depending on exploitability

4. **Validate input sanitization at boundaries**:
   - User-supplied data passed to file paths, shell commands, or database queries
   - Missing length/type/format validation on new API parameters
   - Deserialization of untrusted data without schema validation
   - **Severity: MEDIUM / HIGH**

5. **Review dependency changes** (`requirements.txt`, `pyproject.toml`, `package.json`):
   - New packages with known CVEs (check against advisories)
   - Version downgrades that reintroduce patched vulnerabilities
   - Packages with excessive permissions or suspicious maintainers
   - **Severity: MEDIUM / HIGH**

6. **Check sensitive data handling**:
   - PII or tokens logged to console, files, or telemetry
   - Sensitive fields returned in API responses unnecessarily
   - Telemetry capturing content instead of metadata only
   - **Severity: MEDIUM**

7. **Emit security report**:
   - Overall risk rating: SAFE / LOW RISK / MEDIUM RISK / HIGH RISK / CRITICAL
   - Finding table: `| Severity | File:Line | Issue | Recommendation |`
   - Summary of recommended changes before merge

## Severity Reference

| Level    | Meaning                                           | Action            |
|----------|---------------------------------------------------|-------------------|
| CRITICAL | Immediate exploit or data exposure possible       | Block merge       |
| HIGH     | Significant security weakening                    | Must fix          |
| MEDIUM   | Defense-in-depth gap or likely future risk        | Fix before ship   |
| LOW      | Minor hardening opportunity                       | Address if easy   |
| INFO     | Observation, no direct risk                       | Consider          |
