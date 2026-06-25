## Description

<!-- A concise summary of the changes in this PR. Reference related issues where applicable. -->

Closes #<!-- issue number -->

## Type of Change

<!-- Check all that apply -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] Feature / Enhancement (non-breaking change that adds functionality)
- [ ] Task / Chore (refactor, dependency update, CI, docs, etc.)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)

## Changes Made

<!-- List the key changes introduced by this PR -->

-
-
-

---

## Checklist

### Code Quality

- [ ] Code follows the project's style guidelines
- [ ] `pylint` reports no new errors or warnings (run against changed files under `lib/jnpr/jsnapy/`)

  ```bash
  sudo find ./lib/jnpr/jsnapy -type f -name "*.py" | xargs pylint | grep .
  ```

- [ ] `black` formatting check passes

  ```bash
  black --check --diff --exclude="docs|build|tests|samples|venv" .
  ```

### Unit Tests

- [ ] New or updated unit tests have been added under `tests/unit/`
- [ ] All unit tests pass locally

  ```bash
  cd tests/unit
  nose2 --with-coverage -vvvv
  ```

- [ ] Code coverage has not decreased

### Documentation

- [ ] YAML samples in `samples/` updated or added where applicable
- [ ] `README.md` or wiki references updated (if behaviour changed)

### General

- [ ] No hardcoded credentials, IPs, or sensitive data introduced
- [ ] `requirements.txt` / `development.txt` updated (if new packages were added)
- [ ] I have read [CONTRIBUTING.md](../CONTRIBUTING.md) and my contribution complies with the Apache 2.0 License

---

## Testing Matrix

<!-- Confirm which Python versions and OS combinations you tested locally -->

| Python  | OS            | Pylint | Black | Unit Tests |
|---------|---------------|--------|-------|------------|
| 3.8.x   | ubuntu-latest | [ ]    | [ ]   | [ ]        |
| 3.9.x   | ubuntu-latest | [ ]    | [ ]   | [ ]        |
| 3.10.x  | ubuntu-latest | [ ]    | [ ]   | [ ]        |
| 3.11.x  | ubuntu-latest | [ ]    | [ ]   | [ ]        |
| 3.12.x  | ubuntu-latest | [ ]    | [ ]   | [ ]        |

---

## Additional Notes

<!-- Anything else reviewers should know: deployment considerations, follow-up tasks, known limitations, etc. -->
