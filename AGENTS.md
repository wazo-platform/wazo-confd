# Instructions for agents

## Context

This is the wazo-confd project, a component of the Wazo platform, an IP-PBX solution written in Python and based on the Asterisk PBX.

You are an expert on the Wazo platform and the wazo-confd project.

See the project [README.md](./README.md) for basic information about the project.

## Structure

This project follows the wazo daemon file structure conventions.
See [file-structure.md](https://raw.githubusercontent.com/wazo-platform/wazo-notebook/refs/heads/master/file-structure.md).

## Dependencies

This python project specifies its python dependencies in the [`requirements.txt`](./requirements.txt) file.

## Packaging

This project relies on setuptools for python packaging. See [setup.py](./setup.py) and [setup.cfg](./setup.cfg).

Debian packaging is also supported, see the [debian/](./debian) directory.

## CI

This project has a [Jenkinsfile](./Jenkinsfile) for CI/CD infrastructure in the jenkins.wazo.community domain.

## Docker

This project can be built into a docker image using the [Dockerfile](./Dockerfile).

## Tests

- tox is used to manage python virtual environments for testing, as well as a command runner entrypoint for linters;
- unit tests use the python standard library `unittest` framework, and are scattered in `tests/` directories and `test_*.py` files across the codebase under the `wazo_confd` package;
- integration tests use the pytest framework, along with the `wazo_test_helpers` library, and are scattered in `integration_tests/` directories and `test_*.py` files across the codebase under the `integration_tests` package;

See the project [README.md](./README.md) for information on tests.

### integration tests

See also [integration_tests/README.md](./integration_tests/README.md).

You SHOULD use `tox -eintegration` to run integration tests at least once to make sure the docker images are built.

You MAY use `tox exec -eintegration -- <command>` to run an arbitrary shell command in the integration test virtual environment without rebuilding the docker images, which is faster. In doubt, `tox -eintegration` avoids issues from out-of-date docker images.

## Rules

- you MUST follow Wazo conventions and best practices, as laid out in wazo documentation:
  - [Wazo contribution guide](https://wazo-platform.org/contribute/code/),
  - [REST API guidelines](https://wazo-platform.org/contribute/rest/),
  - [general daemon guidelines](https://wazo-platform.org/uc-doc/contributors/guidelines/),
  - [style guide](https://wazo-platform.org/uc-doc/contributors/style_guide/),
  - [wazo daemon file structure](https://raw.githubusercontent.com/wazo-platform/wazo-notebook/refs/heads/master/file-structure.md);
- you MUST follow the existing structure and conventions of the project, and avoid deviating from them, unless explicitly instructed;
- you CAN suggest improvements to the structure and conventions if relevant to the task at hand;
