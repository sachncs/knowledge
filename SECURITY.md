# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Do not open a public GitHub issue.** Report security vulnerabilities
privately via email:

**sachncs@gmail.com**

You will receive an acknowledgment within 48 hours, and we will work
with you to understand the scope and impact of the issue.

### Response Timeline

| Event                     | Expected Timeframe |
|---------------------------|--------------------|
| Initial acknowledgment    | 48 hours           |
| Triage & investigation    | 5 business days    |
| Fix development           | 10 business days   |
| Patch release             | 15 business days   |

## Disclosure Policy

- We will acknowledge receipt of your report within 48 hours.
- We will confirm the vulnerability and determine its impact within
  5 business days.
- We will release a fix and public advisory as soon as possible,
  coordinated with you if desired.
- Public disclosure is delayed until a fix is available and users
  have had reasonable time to upgrade.

## Security Best Practices for Users

1. **API Keys** — Never hardcode provider API keys. Use environment
   variables (`.env` file, CI secrets, etc.).
2. **Source Validation** — Verify URLs passed to `Knowledge.create()` or
   `fetch_url()` come from trusted sources. The SDK does not validate
   content — it delegates extraction to the configured LLM.
3. **Bundle Integrity** — Use `BundleSerializer.validate()` to check
   that bundle files are structurally consistent after writing.
4. **Updates** — Keep the SDK and its dependencies up to date
   (especially `litellm` and `pydantic`).
5. **Dependency Scanning** — Run `pip-audit` or `safety` on your
   environment to check for known vulnerabilities in dependencies.
