# Dependency Management

This project uses `uv` for Python package management and dependency resolution. Dependencies are defined in `pyproject.toml` and locked in `uv.lock`.

## Dependency Files

### pyproject.toml

The `pyproject.toml` file defines project metadata and dependencies:

- **project.dependencies**: Production dependencies
- **dependency-groups.dev**: Development dependencies
- **dependency-groups.docs**: Documentation dependencies

### uv.lock

The `uv.lock` file contains locked versions of all dependencies and their transitive dependencies, ensuring reproducible installations.

### requirements.txt

The `requirements.txt` file is generated from `uv.lock` and contains only production dependencies for deployment.  This files is generated automatically via `pre-commit hooks` and simplify compatiblity with some systems that have yet to be compliant with `uv` dependencies management.

> **_WARNING:_**  You should not edit the `requirements.txt` file, let the automation handle this file.

If you ever need to generate the `requirements.txt` file manually; here how.

```bash
uv export --no-dev --output-file requirements.txt
```

## Key Dependencies

- **Django 4.2.4**: Web framework
- **pycryptodome 3.18.0**: Cryptographic operations
- **PyYAML 5.3.1**: YAML parsing
- **sqlparse 0.4.2**: SQL parsing utilities

### Documentation Dependencies

- **mkdocs**: Documentation site generator
- **mkdocs-material**: Material theme for mkdocs
