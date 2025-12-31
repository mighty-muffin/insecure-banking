---
hide:
  - toc
---

# Iditarod[^1]

The project is for educational purposes.  These are the instructions for the upcoming demonstration.  It required about 6-8 hours of work to integration, run and accomplished these step with our current tooling.

## Backstage

- [ ] Create an empty repo
- [ ] Commits an empty project structure on the `master` branch, make it the default
- [ ] Create a `main` branch and commits the actual project code
- [ ] Confirm workflows works
- [ ] Create `demo\` branches

## Setup

- [ ] Fork the [insecure-banking](https://github.com/mighty-muffin/insecure-banking) with all branches
- [ ] Read the project documentation
- [ ] Verify everything works
- [ ] Run `make all` from the `Makefile` file is available

## Stage

**SLDC Check (5-10min)**:

This project includes misconfiguration and vulnerabilities in the SDLC; such as there are no dependencies, code or containers scanning included in any [`workflows`](.github/workflows/).

Demonstrate how your platorm can scan and find these issues while providing guidance toward resolution.

> **_NOTE:_**  Use the branch `demo\sdlc` to track change in your fork.

**Dependencies Vulnerabilities (10-15min)**:

This project includes dependencies vulnerabilities in this codebase.  Please demonstrate how SCA scanning capabilities are implemnted on your fork.

The version of [PyYAML@5.3.1](https://pypi.org/project/PyYAML/5.3.1/) included in this project `pyproject.toml` is vulnerable according to [CV-2020-14343](https://nvd.nist.gov/vuln/detail/cve-2020-14343) and [CVE-2020-1747](https://nvd.nist.gov/vuln/detail/cve-2020-1747).  The recommendation is to upgrade PyYAML to version 5.4 or higher.

Demonstrate how your platorm can scan (local & [`branch.yml`](.github/workflows/branch.yml) workflow), prioritize, and find these issues while providing guidance toward resolution.

> **_NOTE:_**  Use the branch `demo\sca` to track change in your fork.

**Exemption & Waivers (10-15min)**:

This project includes severals others dependencies vulnerabilities in this codebase.  It is a legacy platform that has yet been migrate and the Corporate Goons Executives are not willing to invest time and money fixing it.  The CGE have fully accepted these risks and want these silenced until Feb 27th 2026.

Demonstrate how your platorm can generate an exemptions and|or waivers to ignore all others dependencies vulnerabilities.  Showcase local & [`branch.yml`](.github/workflows/branch.yml) workflow) pipeline behave with these exemptions

> **_NOTE:_**  Use the branch `demo\waivers` to track change in your fork.

**Code Vulnerabilities (10-15min)**:

This project includes severals codevulnerabilities in this codebase let's focus on the [`views.p`](src/web/views.py) file. The `get_file_checksum` function is using weak cryptography.

```python
def get_file_checksum(data: bytes) -> str:
    (dk, iv) = (secretKey, secretKey)
    crypter = DES.new(dk, DES.MODE_CBC, iv)
    padded = pad(data, DES.block_size)
    encrypted = crypter.encrypt(padded)
    return base64.b64encode(encrypted).decode("UTF-8")
```

The [Data Encryption Standard (DES](https://en.wikipedia.org/wiki/Data_Encryption_Standard) was officially withdrawn from the NIST recommendation (May 19, 2005), because it no longer provided adequate security (vulnerable to brute-force attacks) and has been replaced by stronger algorithms like the Advanced Encryption Standard (AES).

Demonstrate how your platorm can scan (local & [`branch.yml`](.github/workflows/branch.yml) workflow) and find this issues while providing guidance toward resolution.  Showcase how your platform provide assistance to the end user to resolved this issue.

Implement in the [`branch.yml`](.github/workflows/branch.yml) workflow pipeline incremental vulnerabilities scanning (only check New Code).  Given the project contains several vulnerabiliites, the incremental scan should only be review the code associated with the `get_file_checksum` function and related code.

> **_NOTE:_**  Use the branch `demo\sast` to track change in your fork.

**Container Vulnerabilities (10-15min)**:

This project is a containerized application based around Python3.10-alpine intended to be deployed via some orchestration.

Demonstrate how your platorm can scan and find vulnerablities the [`Dockerfile`](./Dockerfile) and|or the [`PR.yml`](.github/workflows/pr.yml) workflow resulting container binary.  Showcase how your platform can filter the vulnerabilities originating from [upstream base image python:3.10.11-alpine3.18@sha256:def82962a6ee048e54b5bec2fcdfd4aada4a907277ba6b0300f18c836d27f095](https://hub.docker.com/layers/library/python/3.10.11-alpine3.18/images/sha256-afc3587de3a1fed7d55822cedd07238c1803f21fdca609a0352282656a2c144a) versus those create by the project. Implement your platform recommended corrective action and providing guidance toward resolution.

> **_NOTE:_**  Use the branch `demo\container` to track change in your fork.
> **_NOTE:_**  This project must remains on `python3.10.X-alpine-3.XX` version; do not perform a MAJOR upgrade of python or alpine.

## And everything in between

- Showcase what ever you wish to highlight
- If you can not demonstrate a scenario, say so and use the available time on others.
- Leveraging the `pre-commit` framework it is valuable

---

[^1]: The name Iditarod comes from the Deg Xinag and Holikachuk languages of the Athabascan people of Interior Alaska, meaning distant or distant place. It's not only the name of a trail, but also the name of a former town and a river in the same region.
