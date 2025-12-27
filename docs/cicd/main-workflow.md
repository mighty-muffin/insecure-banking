# Main Branch Workflow

## Overview

The main workflow runs on commits to the main branch and handles building, testing, and releasing the application.

## Trigger Events

```yaml
on:
  push:
    branches:
      - main
    paths-ignore:
      - 'README.md'
    tags:
      - v*
```

Triggers on:
- Pushes to main branch
- Version tag creation
- Excludes README.md changes

## Jobs

### 1. Pre-commit

Runs code quality and linting checks.

**Steps:**
- Checkout code
- Run pre-commit hooks (excluding pytest and pin-github-action)

**Timeout:** 5 minutes

### 2. Secret Scanning

Scans for exposed secrets using GitGuardian.

**Steps:**
- Checkout code
- Run GitGuardian scanner
- Continue on error with warning

**Timeout:** 5 minutes

### 3. Build & Unit Test

Builds application and runs test suite.

**Matrix:**
- OS: ubuntu-24.04
- Python: 3.10

**Steps:**
- Checkout code
- Install UV package manager
- Setup Python
- Install dependencies (`uv sync --all-extras --dev --frozen`)
- Run pytest
- Minimize UV cache

**Timeout:** 10 minutes

### 4. Vulnerability Scan

Runs SAST and SCA scanning (placeholders).

**Steps:**
- Checkout code
- Install UV
- Setup Python
- Run SAST (echo placeholder)
- Run SCA (echo placeholder)
- Check scan status

**Timeout:** 10 minutes

### 5. Docker Build & Scan

Builds Docker image and pushes to registry.

**Dependencies:** build, scan, secret jobs

**Steps:**
- Checkout code
- Setup QEMU for multi-platform
- Setup Docker Buildx
- Login to GitHub Container Registry
- Generate Docker metadata (tags, labels)
- Build and push Docker image
  - Platform: linux/amd64
  - Cache: GitHub Actions cache
  - Build args: GIT_COMMIT, REPO_URL
- Run container scan (placeholder)
- Output image tag

**Timeout:** 15 minutes

**Image Tags:**
- `latest` (main branch)
- `sha-<commit>` (main branch)
- Branch name
- PR number
- Git tag

### 6. Gating

Final quality gate check.

**Dependencies:** build, docker jobs

**Steps:**
- Run gating check (echo placeholder)

**Timeout:** 5 minutes

### 7. Release Version

Automated version bumping and release creation.

**Dependencies:** gating, build jobs

**Condition:** Not a version bump commit

**Steps:**
- Checkout with release token
- Setup Python 3.14
- Run Commitizen action
  - Bump version
  - Update changelog
  - Create commit
  - Push changes

**Timeout:** 5 minutes

## Workflow Features

### Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.run_id }}
  cancel-in-progress: true
```

### Permissions

```yaml
permissions:
  contents: read
  packages: write
  pull-requests: write
```

### Conditional Execution

Skip version bump commits:
```yaml
if: ${{ ! startsWith(github.event.head_commit.message, 'bump:') }}
```

## Build Artifacts

- Docker image pushed to GHCR
- Coverage reports (not uploaded)
- Test results (in logs)

## Environment Variables

- `GIT_COMMIT`: Commit SHA
- `REPO_URL`: Repository URL
- `GITHUB_TOKEN`: Automatic token

## Failure Handling

- Pre-commit: Fails pipeline
- Secret scan: Continues with warning
- Build: Continues on error
- Docker: Fails pipeline
- Gating: Fails pipeline
- Release: Fails pipeline

## Related Documentation

- [CI/CD Overview](overview.md)
- [Pull Request Workflow](pr-workflow.md)
- [Tag Workflow](tag-workflow.md)
