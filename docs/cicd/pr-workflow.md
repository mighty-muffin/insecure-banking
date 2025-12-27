# Pull Request Workflow

## Overview

Runs on pull requests to main branch with comprehensive multi-platform testing.

## Trigger Events

```yaml
on:
  pull_request:
    branches:
      - main
    paths-ignore:
      - 'README.md'
```

## Key Differences from Main Workflow

### Multi-Platform Testing

Tests across multiple OS and architectures:

```yaml
matrix:
  fail-fast: false
  os: [ubuntu-22.04, ubuntu-22.04-arm, ubuntu-24.04, ubuntu-24.04-arm]
  python-version: ["3.10"]
```

### No Release Job

PR workflow does not include version release.

### Image Tags

PR-specific Docker tags:
- `gha-<run_id>`
- `pr-<number>`

## Jobs

Same jobs as main workflow except release:
1. Pre-commit
2. Secret scanning
3. Build & Unit Test (multi-platform)
4. Vulnerability scanning
5. Docker build & scan
6. Gating

## Benefits

- Test across platforms before merge
- Catch platform-specific issues
- Validate changes comprehensively
- No production impact

## Related Documentation

- [CI/CD Overview](overview.md)
- [Main Workflow](main-workflow.md)
- [Tag Workflow](tag-workflow.md)
