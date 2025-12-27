# Tag Workflow

## Overview

Triggered on version tag creation to generate releases.

## Trigger Events

```yaml
on:
  push:
    tags:
      - 'v*'
```

Triggers on tags matching `v*` pattern (e.g., v1.0.0, v2.1.3).

## Jobs

### Semantic Release

Single job that generates GitHub release.

**Steps:**

1. Checkout with full history
2. Setup Python 3.14
3. Extract version from tag
4. Read changelog using Commitizen
5. Create changelog for this version
6. Publish GitHub release with changelog

**Timeout:** 5 minutes

## Release Artifacts

- GitHub Release entry
- Release notes from CHANGELOG.md
- Tag reference

## Versioning

Uses semantic versioning (SemVer):
- Major: Breaking changes
- Minor: New features
- Patch: Bug fixes

Format: `v{major}.{minor}.{patch}`

## Related Documentation

- [CI/CD Overview](overview.md)
- [Main Workflow](main-workflow.md)
- [Pull Request Workflow](pr-workflow.md)
