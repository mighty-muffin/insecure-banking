# CI/CD Overview

## Introduction

The Insecure Banking application uses GitHub Actions for continuous integration and continuous deployment. The CI/CD pipeline automates testing, security scanning, Docker image building, and release management.

## Workflow Files

The CI/CD configuration consists of three main workflows located in `.github/workflows/`:

### Main Workflow (`main.yml`)

Runs on pushes to the main branch and tag creation.

**Triggers:**

- Push to `main` branch
- Tag creation (`v*`)
- Excludes README.md changes

**Jobs:**

1. Pre-commit checks
2. Secret scanning
3. Build and unit tests
4. Vulnerability scanning
5. Docker build and scan
6. Gating checks
7. Release version bump

### Pull Request Workflow (`pr.yml`)

Runs on pull requests to main branch.

**Triggers:**

- Pull request to `main` branch
- Excludes README.md changes

**Jobs:**

1. Pre-commit checks
2. Secret scanning
3. Build and unit tests (matrix: multiple OS/arch)
4. Vulnerability scanning
5. Docker build and scan
6. Gating checks

### Tag Workflow (`tag.yml`)

Runs when version tags are created.

**Triggers:**

- Tag push (`v*`)

**Jobs:**

1. Generate changelog
2. Create GitHub release

## CI/CD Pipeline Stages

### Stage 1: Pre-commit Validation

Runs linting and code quality checks:

- YAML linting
- Markdown linting
- JSON validation
- Python formatting (ruff)
- End-of-file fixes
- Trailing whitespace removal

### Stage 2: Security Scanning

Multiple security checks:

- **Secret Scanning**: GitGuardian detects exposed secrets
- **SAST**: Static Application Security Testing (placeholder)
- **SCA**: Software Composition Analysis (placeholder)

### Stage 3: Build and Test

Builds application and runs test suite:

- Install dependencies with uv
- Run pytest with coverage
- Generate coverage reports
- Test on multiple platforms (PR workflow)

### Stage 4: Docker

Builds and scans container images:

- Multi-stage Docker build
- Push to GitHub Container Registry (GHCR)
- Container vulnerability scanning (placeholder)
- Multi-architecture support (linux/amd64)

### Stage 5: Gating

Final quality gate before deployment or release.

### Stage 6: Release (Main workflow only)

Automated version management:

- Commitizen for semantic versioning
- Automated changelog generation
- Git tag creation
- GitHub release creation

## Pipeline Architecture

```text
Push/PR Event
     ↓
┌────────────────┐
│  Pre-commit    │
└────────────────┘
     ↓
┌────────────────┐
│ Secret Scan    │
└────────────────┘
     ↓
┌────────────────┐┌────────────────┐
│  Build & Test  ││ Vuln Scanning  │
└────────────────┘└────────────────┘
     ↓
┌────────────────┐
│ Docker Build   │
└────────────────┘
     ↓
┌────────────────┐
│    Gating      │
└────────────────┘
     ↓
┌────────────────┐
│  Release (*)   │
└────────────────┘
```

\* Main branch only

## Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.run_id }}
  cancel-in-progress: true
```

**Behavior:**

- Cancels in-progress runs for same branch
- Prevents resource waste
- Faster feedback for latest changes

## Permissions

```yaml
permissions:
  contents: read
  packages: write
  pull-requests: write
```

**Scope:**

- **contents**: Read repository contents
- **packages**: Push Docker images to GHCR
- **pull-requests**: Comment on PRs

## Environment Variables

### Build Arguments

```yaml
build-args: |
  BUILDKIT_INLINE_CACHE=1
  GIT_COMMIT=${{ github.sha }}
  REPO_URL=${{ github.server_url }}/${{ github.repository }}
```

### Runtime Environment

Set during workflow execution:

- Python version: 3.10 (tests), 3.14 (release)
- uv version: 0.9.0 / 0.9.18
- Node environment (for pre-commit hooks)

## Caching Strategy

### Docker Layer Caching

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

Uses GitHub Actions cache for Docker layers.

### UV Cache

```yaml
with:
  enable-cache: true
  cache-dependency-glob: "uv.lock"
```

Caches Python dependencies.

## Matrix Strategy

Pull request workflow tests across multiple platforms:

```yaml
strategy:
  fail-fast: false
  matrix:
    os: [ubuntu-22.04, ubuntu-22.04-arm, ubuntu-24.04, ubuntu-24.04-arm]
    python-version: ["3.10"]
```

**Platforms:**

- x86-64: ubuntu-22.04, ubuntu-24.04
- ARM64: ubuntu-22.04-arm, ubuntu-24.04-arm

## Artifact Management

### Docker Images

Images pushed to GitHub Container Registry:

- Registry: `ghcr.io`
- Repository: `ghcr.io/mighty-muffin/insecure-banking`
- Tags: latest, branch name, PR number, SHA

### Coverage Reports

Generated but not uploaded:

- HTML coverage report
- XML coverage report

## Secrets Management

Required secrets:

- `GITHUB_TOKEN`: Automatically provided
- `GITGUARDIAN_API_KEY`: GitGuardian secret scanning
- `RELEASE_PAT`: Personal access token for releases

## Failure Handling

### Continue on Error

Some steps continue on failure:

```yaml
continue-on-error: true
```

Applied to:

- Unit tests
- Secret scanning

### Strict Failures

Other steps fail pipeline:

- Pre-commit checks
- Docker build
- Gating

## Notifications

No explicit notifications configured. GitHub provides:

- Pull request status checks
- Email notifications
- GitHub UI status

## Best Practices

The CI/CD pipeline follows best practices:

1. **Security First**: Secret and vulnerability scanning
2. **Fast Feedback**: Parallel execution and caching
3. **Reproducible Builds**: Locked dependencies
4. **Container Security**: Multi-stage builds
5. **Automated Testing**: Comprehensive test suite
6. **Version Control**: Semantic versioning
7. **Documentation**: Automated changelog

## Performance Optimization

- Parallel test execution
- Docker layer caching
- Dependency caching
- Matrix strategy parallelization
- Minimal install steps

## Monitoring

Monitor pipeline through:

- GitHub Actions UI
- Workflow run logs
- Status badges
- Pull request checks

## Related Documentation

- [Main Workflow](main-workflow.md)
- [Pull Request Workflow](pr-workflow.md)
- [Tag Workflow](tag-workflow.md)
- [Pre-commit Hooks](pre-commit.md)
- [Docker Containerization](../development/docker.md)
